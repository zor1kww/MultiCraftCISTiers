# -*- coding: utf-8 -*-
"""
Отмена результата тестирования кнопкой в группе тестеров.

Как это работает
----------------
1. main.process_result записывает результат в players.js. Внутри mutate()
   он делает копию списка игроков ДО и сравнивает с состоянием ПОСЛЕ
   (diff_players): для каждого затронутого игрока (сам игрок, оппоненты,
   кто-то из них с автопонижением) запоминается, что именно изменилось -
   тир/штраф по конкретным китам, добавленные записи matchHistory, регион,
   факт создания игрока. Так снимок не зависит от штрафной логики: что бы
   она ни сделала, откат вернёт ровно прежнее состояние.
2. Снимок сохраняется в отдельный файл bot_data/undo_log.json в репозитории
   (диск на Render временный, поэтому не локально). Формат players.js
   этим не затрагивается.
3. В топик тестеров (SOURCE_CHAT_ID / SOURCE_THREAD_ID) бот отвечает на
   исходное сообщение с кнопкой "Отменить результат". Кнопку может нажать
   любой участник этой группы (доступ проверяется по chat.id сообщения с
   кнопкой, а не по ADMIN_IDS). Перед откатом - шаг подтверждения
   (CONFIRM_BEFORE_UNDO).
4. Откат (apply_undo): сначала ПРОВЕРКА без изменений - игрок на месте и
   по затронутым китам тир/штраф всё ещё равны состоянию "после" этого
   результата; если нет (был следующий результат, правка админа,
   переименование) - откат отклоняется, чтобы не затереть более свежие
   данные. Потом откат: возвращаются тиры/штрафы/регион, удаляются
   добавленные записи matchHistory (у ВСЕХ участников - лог дуэлей на
   сайте читает players.js, поэтому обновляется сам), созданный этим
   результатом пустой игрок удаляется.
5. Публичные карточки результата/понижения помечаются "отменён".

Ограничения: отмена возможна UNDO_WINDOW_HOURS часов и один раз.
"""

import base64
import copy
import json
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone

import requests
from telebot import types

import github_storage
import reactions
from bot_config import SOURCE_CHAT_ID, SOURCE_THREAD_ID


# ==========================================
# НАСТРОЙКИ
# ==========================================

UNDO_LOG_PATH = "bot_data/undo_log.json"
UNDO_WINDOW_HOURS = 24        # сколько часов после записи доступна отмена
UNDO_KEEP_DAYS = 7            # сколько дней хранить записи в undo_log.json
UNDO_MAX_RECORDS = 200        # жёсткий потолок размера лога
CONFIRM_BEFORE_UNDO = True    # двухшаговая отмена: кнопка -> "Да, отменить"

MAX_RETRIES = github_storage.MAX_RETRIES
RETRY_DELAY_SECONDS = github_storage.RETRY_DELAY_SECONDS


class UndoStorageError(Exception):
    pass


class UndoConflict(Exception):
    """Откат невозможен без риска затереть более свежие данные."""
    pass


# ==========================================
# ЧИСТАЯ ЛОГИКА: снимок и откат (без Telegram и GitHub)
# ==========================================

def _find(players_list, name):
    lname = str(name).lower()
    for p in players_list:
        if str(p.get('name', '')).lower() == lname:
            return p
    return None


def diff_players(before_list, after_list):
    """
    Сравнивает списки игроков ДО и ПОСЛЕ применения результата и возвращает
    список изменений по затронутым игрокам (чистый JSON):

      {
        "name": "...", "created": bool,
        "kits": {kit: {"tier_before", "tier_after", "pen_before", "pen_after"}},
        "added_history": [entry, ...],          # добавленные в конец matchHistory
        "region": {"before": ..., "after": ...} # только если менялся
      }

    None в *_before/*_after означает "записи по этому киту не было".
    """
    before_by_name = {str(p.get('name', '')).lower(): p for p in before_list}
    changes = []

    for after in after_list:
        name = after.get('name', '')
        before = before_by_name.get(str(name).lower())
        created = before is None
        b = before or {}

        b_tiers, a_tiers = b.get('tiers') or {}, after.get('tiers') or {}
        b_pen, a_pen = b.get('penaltyByKit') or {}, after.get('penaltyByKit') or {}

        kits = {}
        for kit in set(b_tiers) | set(a_tiers) | set(b_pen) | set(a_pen):
            tb, ta = b_tiers.get(kit), a_tiers.get(kit)
            pb, pa = b_pen.get(kit), a_pen.get(kit)
            if tb != ta or pb != pa:
                kits[kit] = {
                    "tier_before": copy.deepcopy(tb), "tier_after": copy.deepcopy(ta),
                    "pen_before": copy.deepcopy(pb), "pen_after": copy.deepcopy(pa),
                }

        b_hist = b.get('matchHistory') or []
        a_hist = after.get('matchHistory') or []
        added = copy.deepcopy(a_hist[len(b_hist):])

        region_changed = b.get('region') != after.get('region')

        if not (created or kits or added or region_changed):
            continue

        change = {"name": name, "created": created, "kits": kits, "added_history": added}
        if region_changed:
            change["region"] = {"before": b.get('region'), "after": after.get('region')}
        changes.append(change)

    # Гарантируем "чистый JSON" (кортежи -> списки и т.п.), чтобы снимок,
    # записанный в файл, ничем не отличался от прочитанного обратно.
    return json.loads(json.dumps(changes, ensure_ascii=False))


def _restore(container, key, old_value):
    if old_value is None:
        container.pop(key, None)
    else:
        container[key] = copy.deepcopy(old_value)


def apply_undo(players_list, changes):
    """
    Откатывает изменения из diff_players. Мутирует players_list.

    Сначала проверяет ВСЕ изменения и при любом конфликте бросает
    UndoConflict, ничего не изменив. Безопасно вызывать повторно на
    свежих данных (github_storage может перезапустить mutate при
    sha-конфликте).
    """
    resolved = []
    for ch in changes:
        player = _find(players_list, ch["name"])
        if player is None:
            raise UndoConflict(f"игрок {ch['name']} не найден (удалён или переименован)")
        tiers = player.get('tiers') or {}
        pens = player.get('penaltyByKit') or {}
        for kit, st in ch["kits"].items():
            if tiers.get(kit) != st["tier_after"] or pens.get(kit) != st["pen_after"]:
                raise UndoConflict(
                    f"у {ch['name']} по киту {kit} уже были другие изменения после этого результата"
                )
        resolved.append((player, ch))

    for player, ch in resolved:
        tiers = player.setdefault('tiers', {})
        pens = player.setdefault('penaltyByKit', {})
        for kit, st in ch["kits"].items():
            _restore(tiers, kit, st["tier_before"])
            _restore(pens, kit, st["pen_before"])

        # Удаляем добавленные записи с конца (новые записи всегда в конце).
        # Если запись уже удалена админом - это не конфликт, пропускаем.
        hist = player.setdefault('matchHistory', [])
        for entry in ch["added_history"]:
            for i in range(len(hist) - 1, -1, -1):
                if hist[i] == entry:
                    del hist[i]
                    break

        reg = ch.get("region")
        if reg and player.get('region') == reg["after"]:
            if reg["before"] is None:
                player.pop('region', None)
            else:
                player['region'] = reg["before"]

        # Игрок, созданный этим результатом и оставшийся пустым, удаляется
        if ch["created"] and not player.get('tiers') and not player.get('matchHistory') \
                and not player.get('penaltyByKit'):
            players_list[:] = [p for p in players_list if p is not player]

    return players_list


# ==========================================
# ХРАНИЛИЩЕ СНИМКОВ (bot_data/undo_log.json в GitHub)
# ==========================================

def _log_url(gh_repo):
    return f"https://api.github.com/repos/{gh_repo}/contents/{UNDO_LOG_PATH}"


def _get_log(gh_repo, gh_token):
    """Возвращает (data, sha). Если файла ещё нет - (пустой лог, None)."""
    headers = {"Authorization": f"token {gh_token}"}
    response = requests.get(_log_url(gh_repo), headers=headers, timeout=15)
    if response.status_code == 404:
        return {"records": {}}, None
    if response.status_code != 200:
        raise UndoStorageError(f"Ошибка GitHub при чтении undo_log: {response.status_code}")

    file_data = response.json()
    try:
        data = json.loads(base64.b64decode(file_data['content']).decode('utf-8'))
    except ValueError as e:
        # Не перезаписываем молча повреждённый лог - пусть разберутся руками
        raise UndoStorageError(f"undo_log.json повреждён: {e}")
    if not isinstance(data, dict):
        raise UndoStorageError("undo_log.json имеет неожиданный формат")
    data.setdefault("records", {})
    return data, file_data['sha']


def _put_log(gh_repo, gh_token, data, sha, message):
    headers = {"Authorization": f"token {gh_token}"}
    text = json.dumps(data, indent=2, ensure_ascii=False)
    payload = {
        "message": message,
        "content": base64.b64encode(text.encode('utf-8')).decode('utf-8'),
    }
    if sha:
        payload["sha"] = sha
    return requests.put(_log_url(gh_repo), headers=headers, json=payload, timeout=15)


def _update_log(gh_repo, gh_token, mutate_fn, message):
    """Read-modify-write undo_log.json с retry на sha-конфликт (как в github_storage)."""
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            data, sha = _get_log(gh_repo, gh_token)
            data = mutate_fn(data)
            response = _put_log(gh_repo, gh_token, data, sha, message)
            if response.status_code in (200, 201):
                return data
            if response.status_code in (409, 422):
                last_error = f"sha-конфликт (попытка {attempt}/{MAX_RETRIES})"
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            raise UndoStorageError(f"Ошибка записи undo_log: {response.status_code} {response.text[:200]}")
        except UndoStorageError:
            raise
        except requests.RequestException as e:
            last_error = f"Сетевая ошибка: {e}"
            time.sleep(RETRY_DELAY_SECONDS)
    raise UndoStorageError(f"Не удалось записать undo_log: {last_error}")


def _now():
    return datetime.now(timezone.utc)


def _prune(data):
    """Выкидывает старые записи и держит размер лога в пределах потолка."""
    cutoff = _now() - timedelta(days=UNDO_KEEP_DAYS)
    records = data.get("records", {})

    def created(rec):
        try:
            return datetime.fromisoformat(rec["created_at"])
        except (KeyError, ValueError, TypeError):
            return datetime.min.replace(tzinfo=timezone.utc)

    kept = {rid: rec for rid, rec in records.items() if created(rec) >= cutoff}
    if len(kept) > UNDO_MAX_RECORDS:
        newest = sorted(kept.items(), key=lambda kv: created(kv[1]), reverse=True)[:UNDO_MAX_RECORDS]
        kept = dict(newest)
    data["records"] = kept
    return data


def _is_expired(rec):
    try:
        created = datetime.fromisoformat(rec["created_at"])
    except (KeyError, ValueError, TypeError):
        return True
    return _now() - created > timedelta(hours=UNDO_WINDOW_HOURS)


# ==========================================
# TELEGRAM: кнопка в группе тестеров
# ==========================================

def _ask_keyboard(record_id):
    kb = types.InlineKeyboardMarkup()
    first_action = "ask" if CONFIRM_BEFORE_UNDO else "do"
    kb.add(types.InlineKeyboardButton("↩️ Отменить результат", callback_data=f"undo:{first_action}:{record_id}"))
    return kb


def _confirm_keyboard(record_id):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ Да, отменить", callback_data=f"undo:do:{record_id}"),
        types.InlineKeyboardButton("⬅️ Оставить", callback_data=f"undo:keep:{record_id}"),
    )
    return kb


def _user_label(user):
    if user is None:
        return "неизвестный"
    if getattr(user, "username", None):
        return f"@{user.username}"
    return getattr(user, "first_name", None) or str(getattr(user, "id", "?"))


def _safe_edit_text(bot, chat_id, message_id, text, reply_markup=None):
    try:
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
    except Exception as e:
        print(f"[undo] Не удалось отредактировать сообщение {chat_id}/{message_id}: {e}")


def _safe_edit_markup(bot, chat_id, message_id, reply_markup):
    try:
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
    except Exception as e:
        print(f"[undo] Не удалось обновить кнопки {chat_id}/{message_id}: {e}")


def offer_undo(bot, gh_repo, gh_token, label, changes, card_refs, source_message_id):
    """
    Сохраняет снимок и отправляет в топик тестеров ответ с кнопкой отмены.
    НИКОГДА не бросает исключений наружу: сбой отмены не должен ломать
    основной поток записи результатов. Если снимок сохранить не удалось,
    сообщение отправляется без кнопки.
    """
    keyboard = None
    text = f"✅ Записано: {label}"

    try:
        if changes:
            record_id = uuid.uuid4().hex[:10]
            record = {
                "id": record_id,
                "created_at": _now().isoformat(),
                "label": label,
                "status": "active",
                "changes": changes,
                "cards": card_refs,
            }

            def add_record(data):
                data["records"][record_id] = record
                return _prune(data)

            _update_log(gh_repo, gh_token, add_record, f"undo-log: +{record_id} {label}"[:200])
            keyboard = _ask_keyboard(record_id)
            text += f"\nОшиблись? Любой участник группы может отменить результат в течение {UNDO_WINDOW_HOURS} ч."
    except Exception as e:
        print(f"[undo] Не удалось сохранить снимок для отмены: {e}")
        text += "\n(отмена для этого результата недоступна)"

    kwargs = {"chat_id": SOURCE_CHAT_ID, "text": text}
    if SOURCE_THREAD_ID is not None:
        kwargs["message_thread_id"] = SOURCE_THREAD_ID
    if keyboard is not None:
        kwargs["reply_markup"] = keyboard

    try:
        try:
            bot.send_message(reply_to_message_id=source_message_id, **kwargs)
        except Exception:
            # Например, исходное сообщение удалено - шлём без привязки к нему
            bot.send_message(**kwargs)
    except Exception as e:
        print(f"[undo] Не удалось отправить сообщение с кнопкой отмены: {e}")


_undo_lock = threading.Lock()


def register(bot, gh_repo, gh_token):
    """Регистрирует обработчик кнопок undo:*. Вызывать один раз при старте."""

    @bot.callback_query_handler(func=lambda c: bool(c.data) and c.data.startswith('undo:'))
    def on_undo_callback(call):
        try:
            _handle_callback(bot, gh_repo, gh_token, call)
        except Exception as e:
            print(f"[undo] Ошибка обработчика отмены: {e}")
            try:
                bot.answer_callback_query(call.id, "Ошибка отмены, подробности в логах бота.", show_alert=True)
            except Exception:
                pass


def _handle_callback(bot, gh_repo, gh_token, call):
    parts = (call.data or "").split(':')
    if len(parts) != 3:
        bot.answer_callback_query(call.id)
        return
    _, action, record_id = parts

    msg = call.message
    # Только кнопки, стоящие в группе тестеров (любой её участник)
    if msg is None or msg.chat.id != SOURCE_CHAT_ID:
        bot.answer_callback_query(call.id, "Отмена доступна только в группе тестеров.", show_alert=True)
        return

    chat_id, message_id = msg.chat.id, msg.message_id

    if action == "ask":
        _safe_edit_markup(bot, chat_id, message_id, _confirm_keyboard(record_id))
        bot.answer_callback_query(call.id, "Отменить результат? Подтвердите.")
        return

    if action == "keep":
        _safe_edit_markup(bot, chat_id, message_id, _ask_keyboard(record_id))
        bot.answer_callback_query(call.id)
        return

    if action != "do":
        bot.answer_callback_query(call.id)
        return

    bot.answer_callback_query(call.id, "Отменяю…")
    with _undo_lock:
        _perform_undo(bot, gh_repo, gh_token, record_id, call.from_user, chat_id, message_id)


def _perform_undo(bot, gh_repo, gh_token, record_id, user, chat_id, message_id):
    who = _user_label(user)

    try:
        data, _ = _get_log(gh_repo, gh_token)
    except Exception as e:
        _safe_edit_text(bot, chat_id, message_id,
                        f"⚠️ Не удалось прочитать данные для отмены: {e}\nПопробуйте позже.",
                        _ask_keyboard(record_id))
        return

    rec = data["records"].get(record_id)
    if rec is None:
        _safe_edit_text(bot, chat_id, message_id, "⚠️ Запись для отмены не найдена (устарела).")
        return
    if rec.get("status") == "undone":
        _safe_edit_text(bot, chat_id, message_id,
                        f"↩️ Результат уже отменён: {rec['label']}\nОтменил: {rec.get('undone_by', '?')}")
        return
    if _is_expired(rec):
        _safe_edit_text(bot, chat_id, message_id,
                        f"⌛ Срок отмены ({UNDO_WINDOW_HOURS} ч) истёк: {rec['label']}\n"
                        f"Исправьте вручную через /admin.")
        return

    def mutate(players_list):
        apply_undo(players_list, rec["changes"])
        return players_list

    try:
        github_storage.update_players_file(gh_repo, gh_token, mutate, f"undo: {rec['label']}"[:200])
    except UndoConflict as e:
        _safe_edit_text(bot, chat_id, message_id,
                        f"⚠️ Отмена невозможна: {e}.\nИсправьте вручную через /admin.")
        return
    except github_storage.GithubStorageError as e:
        _safe_edit_text(bot, chat_id, message_id,
                        f"⚠️ Не удалось записать отмену на GitHub: {e}\nМожно попробовать ещё раз.",
                        _ask_keyboard(record_id))
        return

    def mark_undone(log_data):
        target = log_data["records"].get(record_id)
        if target is not None:
            target["status"] = "undone"
            target["undone_by"] = who
            target["undone_at"] = _now().isoformat()
        return log_data

    try:
        _update_log(gh_repo, gh_token, mark_undone, f"undo-log: undone {record_id}")
    except Exception as e:
        # Данные уже откатаны; повторное нажатие упрётся в проверку конфликта
        print(f"[undo] Результат откатан, но отметку в undo_log записать не удалось: {e}")

    _safe_edit_text(bot, chat_id, message_id, f"↩️ Результат отменён: {rec['label']}\nОтменил: {who}")

    for ref in rec.get("cards", []):
        _safe_edit_text(bot, ref["chat_id"], ref["message_id"], f"❌ Результат отменён: {rec['label']}")
        reactions.set_reaction(bot, ref["chat_id"], ref["message_id"], None)  # снимаем реакцию
