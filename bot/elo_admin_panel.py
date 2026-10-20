"""
Telegram-панель администратора эло-системы (команда /elo_admin в личке с
ботом). Работает в потоке Telegram-бота, а к базе обращается через
db_executor - то есть выполняет действия в потоке Discord, которому
принадлежит соединение с Turso.

Доступ: Telegram-ID из ADMIN_IDS старой админ-панели (admin_panel.py) и/или
из переменной окружения ELO_ADMIN_IDS (через запятую). Остальным панель
не отвечает.

Все callback_data начинаются с "ea:" и укладываются в лимит Telegram
(64 байта): игроки и дуэли передаются по числовому id, киты - по индексу
в elo_admin_actions.KITS.
"""

import os
from typing import Optional

from telebot import types

import db_executor
import elo_admin_actions as A
from handlers import ALLOWED_REGIONS

PREFIX = "ea:"
_DEVICE_LABEL = {"PC": "PC", "MOBILE": "мобильный", None: "не отмечено"}


def _load_admin_ids() -> set:
    ids = set()
    try:
        import admin_panel  # старая панель: ADMIN_IDS захардкожен там
        ids |= {int(x) for x in getattr(admin_panel, "ADMIN_IDS", ()) or ()}
    except Exception as e:
        print(f"[elo-admin] ADMIN_IDS из admin_panel не получены: {e}")
    for raw in os.environ.get("ELO_ADMIN_IDS", "").split(","):
        raw = raw.strip()
        if raw.isdigit():
            ids.add(int(raw))
    return ids


def _fmt_elo(value: float) -> str:
    return f"{value:g}"


def _minus(text: str) -> str:
    return text.replace("-", "\u2212")


def card_text(card: dict) -> str:
    lines = [
        f"\U0001F464 {card['name']}",
        f"Регион: {card['region'] or '?'} \u00b7 Устройство: {_DEVICE_LABEL.get(card['device'], card['device'])}",
        "Статус: " + ("скрыт из топа" if card["removed"] else "активен")
        + ("" if card["device"] != "PC" else " (PC - в топе не показывается)"),
        "",
        "Эло по китам:",
    ]
    if card["ratings"]:
        lines += [f"{r['kit']} \u2014 {_fmt_elo(r['elo'])} ({r['tier']})" for r in card["ratings"]]
    else:
        lines.append("пока нет рейтингов")
    if card["matches"]:
        lines += ["", "Последние дуэли:"]
        for m in card["matches"]:
            lines.append(f"#{m['id']} {m['kit']}: {m['winner']} победил {m['loser']} "
                         f"(+{m['winner_delta']}/{_minus('-' + str(m['loser_delta']))})")
    return "\n".join(lines)


def register(bot, admin_ids: Optional[set] = None):
    ids = set(admin_ids) if admin_ids is not None else _load_admin_ids()
    if not ids:
        print("[elo-admin] админов нет (ADMIN_IDS / ELO_ADMIN_IDS) - панель никому не будет отвечать")

    # ---------- вспомогательное ----------

    def is_admin(user) -> bool:
        return user is not None and user.id in ids

    def admin_label(user) -> str:
        return f"{user.id}" + (f" (@{user.username})" if getattr(user, "username", None) else "")

    def call_db(fn):
        """(True, результат) или (False, текст ошибки для админа)."""
        try:
            return True, db_executor.run_on_db_thread(fn)
        except TimeoutError:
            return False, ("Бот эло-системы сейчас не отвечает (Discord-поток не запущен или "
                           "перегружен). Действие НЕ выполнено, попробуйте позже.")
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Ошибка: {e}"

    def show(chat_id, text, markup=None, call=None):
        if call is not None:
            try:
                bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)
                return
            except Exception as e:
                if "not modified" in str(e).lower():
                    return
        bot.send_message(chat_id, text, reply_markup=markup)

    def kb(rows):
        markup = types.InlineKeyboardMarkup()
        for row in rows:
            markup.row(*[types.InlineKeyboardButton(text, callback_data=data) for text, data in row])
        return markup

    def btn(text, *parts):
        return (text, PREFIX + ":".join(str(p) for p in parts))

    # ---------- экраны ----------

    def menu_screen(chat_id, call=None):
        show(chat_id, "Админ-панель эло-системы", kb([
            [btn("\U0001F50E Найти игрока", "find")],
            [btn("\U0001F558 Последние дуэли", "ml")],
            [btn("\u2699\uFE0F Настройки", "st")],
            [btn("\U0001F4DC Журнал действий", "lg")],
        ]), call)

    def card_screen(chat_id, player_id, call=None, prefix_note: str = ""):
        ok, card = call_db(lambda conn: A.player_card(conn, player_id))
        if not ok or card is None:
            show(chat_id, card if not ok else "Игрок не найден.", kb([[btn("\u2B05 Меню", "menu")]]), call)
            return
        pid = card["id"]
        rows = [
            [btn("\u270F\uFE0F Изменить эло", "ek", pid), btn("\u267B\uFE0F Сбросить эло", "rk", pid)],
            [btn("\U0001F30D Регион", "rg", pid)],
            [btn("\U0001F5A5 PC", "dv", pid, "PC"), btn("\U0001F4F1 Мобильный", "dv", pid, "MOBILE")],
            [btn("\u2705 Вернуть в топ", "rs", pid) if card["removed"] else btn("\U0001F6AB Скрыть из топа", "rm", pid)],
            [btn("\u2B05 Меню", "menu")],
        ]
        show(chat_id, (prefix_note + "\n\n" if prefix_note else "") + card_text(card), kb(rows), call)

    def kits_screen(chat_id, call, player_id, action, title):
        ok, card = call_db(lambda conn: A.player_card(conn, player_id))
        if not ok or card is None:
            show(chat_id, card if not ok else "Игрок не найден.", None, call)
            return
        rated = {r["kit"]: r["elo"] for r in card["ratings"]}
        buttons = [btn(f"{kit} ({_fmt_elo(rated[kit])})" if kit in rated else kit, action, player_id, i)
                   for i, kit in enumerate(A.KITS)]
        rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
        rows.append([btn("\u2B05 Назад", "pc", player_id)])
        show(chat_id, f"{card['name']}: {title}", kb(rows), call)

    def matches_screen(chat_id, call=None):
        ok, matches = call_db(lambda conn: A.recent_matches(conn, 10))
        if not ok:
            show(chat_id, matches, kb([[btn("\u2B05 Меню", "menu")]]), call)
            return
        if not matches:
            show(chat_id, "Завершённых дуэлей пока нет.", kb([[btn("\u2B05 Меню", "menu")]]), call)
            return
        rows = [[btn(f"#{m['id']} {m['kit']}: {m['winner']} > {m['loser']}", "md", m["id"])] for m in matches]
        rows.append([btn("\u2B05 Меню", "menu")])
        show(chat_id, "Последние дуэли (нажмите, чтобы открыть):", kb(rows), call)

    def match_screen(chat_id, match_id, call=None):
        ok, d = call_db(lambda conn: A.match_details(conn, match_id))
        if not ok or d is None:
            show(chat_id, d if not ok else "Дуэль не найдена.", kb([[btn("\u2B05 К дуэлям", "ml")]]), call)
            return
        if d["status"] != "finished":
            text = f"Дуэль #{match_id} ({d['kit']}): статус {d['status']}."
            rows = [[btn("\u2B05 К дуэлям", "ml")]]
        else:
            text = (f"Дуэль #{match_id} \u00b7 {d['kit']}\n"
                    f"{d['winner']} победил {d['loser']}\n"
                    f"{d['winner']}: {_fmt_elo(d['winner_before'])} \u2192 {_fmt_elo(d['winner_elo_after'])} (+{d['winner_delta']})\n"
                    f"{d['loser']}: {_fmt_elo(d['loser_before'])} \u2192 {_fmt_elo(d['loser_elo_after'])} ({_minus('-' + str(d['loser_delta']))})\n"
                    f"Причина: {'смерть' if d['end_reason'] == 'death' else 'не вернулся за 3 минуты' if d['end_reason'] == 'timeout' else d['end_reason']}\n"
                    f"Окончена: {d['finished_at']}")
            rows = [[btn("\u274C Аннулировать дуэль", "vq", match_id)], [btn("\u2B05 К дуэлям", "ml")]]
        show(chat_id, text, kb(rows), call)

    def settings_screen(chat_id, call=None):
        ok, st = call_db(lambda conn: A.settings_state(conn))
        if not ok:
            show(chat_id, st, kb([[btn("\u2B05 Меню", "menu")]]), call)
            return
        tg = ("включена" if st["tg_enabled"] else "выключена") + ("" if st["tg_possible"] else " (нет TG_TOKEN)")
        text = (f"Настройки\n\nМножитель эло за победу: \u00d7{st['win_bonus']}\n"
                f"Публикация результатов в Telegram: {tg}")
        rows = [
            [btn("Победа \u00d71", "sb", 1), btn("Победа \u00d72", "sb", 2)],
            [btn("Публикация: вкл", "sg", 1), btn("Публикация: выкл", "sg", 0)],
            [btn("\u2B05 Меню", "menu")],
        ]
        show(chat_id, text, kb(rows), call)

    def log_screen(chat_id, call=None):
        ok, entries = call_db(lambda conn: A.recent_log(conn, 10))
        if not ok:
            show(chat_id, entries, kb([[btn("\u2B05 Меню", "menu")]]), call)
            return
        text = "Журнал действий (последние 10):\n\n" + (
            "\n".join(f"{e['ts'][:16].replace('T', ' ')} \u00b7 {e['admin']} \u00b7 {e['action']}: {e['details']}"
                      for e in entries) if entries else "пусто")
        show(chat_id, text, kb([[btn("\u2B05 Меню", "menu")]]), call)

    # ---------- ввод текстом ----------

    def ask(chat_id, prompt, handler, *args):
        msg = bot.send_message(chat_id, prompt + "\n(/cancel - отмена)")
        bot.register_next_step_handler(msg, handler, *args)

    def cancelled(message) -> bool:
        if message.text and message.text.strip().startswith("/"):
            bot.send_message(message.chat.id, "Отменено.")
            return True
        return False

    def on_nick(message):
        if not is_admin(message.from_user) or cancelled(message):
            return
        query = (message.text or "").strip()
        ok, pid = call_db(lambda conn: A.resolve_player(conn, query))
        if not ok:
            bot.send_message(message.chat.id, pid)
        elif pid is None:
            bot.send_message(message.chat.id, f"Игрок «{query}» не найден. Проверьте ник.",
                             reply_markup=kb([[btn("\U0001F50E Искать снова", "find"), btn("\u2B05 Меню", "menu")]]))
        else:
            card_screen(message.chat.id, pid)

    def on_elo_value(message, player_id, kit_index):
        if not is_admin(message.from_user) or cancelled(message):
            return
        kit = A.KITS[kit_index]
        try:
            value = float((message.text or "").strip().replace(",", "."))
        except ValueError:
            ask(message.chat.id, f"Нужно число от 0 до {A.MAX_ELO}. Новое эло для {kit}:", on_elo_value, player_id, kit_index)
            return
        admin = admin_label(message.from_user)
        ok, res = call_db(lambda conn: A.set_player_elo(conn, admin, player_id, kit, value))
        if not ok:
            bot.send_message(message.chat.id, res)
            return
        card_screen(message.chat.id, player_id, prefix_note=f"\u2705 {kit}: {_fmt_elo(res[0])} \u2192 {_fmt_elo(res[1])}")

    # ---------- обработчики ----------

    @bot.message_handler(commands=["elo_admin"])
    def cmd_elo_admin(message):
        if message.chat.type != "private" or not is_admin(message.from_user):
            return
        menu_screen(message.chat.id)

    @bot.callback_query_handler(func=lambda c: c.data and c.data.startswith(PREFIX))
    def on_callback(call):
        if not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "Нет доступа")
            return
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        parts = call.data[len(PREFIX):].split(":")
        action, args = parts[0], parts[1:]
        admin = admin_label(call.from_user)

        try:
            if action == "menu":
                menu_screen(chat_id, call)
            elif action == "find":
                ask(chat_id, "Пришлите ник игрока:", on_nick)
            elif action == "pc":                       # вернуться к карточке
                card_screen(chat_id, int(args[0]), call)
            elif action == "ek":                       # выбрать кит для правки эло
                kits_screen(chat_id, call, int(args[0]), "ep", "выберите кит для изменения эло")
            elif action == "ep":                       # кит выбран -> спросить значение
                pid, ki = int(args[0]), int(args[1])
                ask(chat_id, f"Новое эло для {A.KITS[ki]} (число от 0 до {A.MAX_ELO}):", on_elo_value, pid, ki)
            elif action == "rk":                       # выбрать кит для сброса
                kits_screen(chat_id, call, int(args[0]), "rq", "выберите кит для сброса до 1000")
            elif action == "rq":                       # подтверждение сброса
                pid, ki = int(args[0]), int(args[1])
                show(chat_id, f"Сбросить эло на ките {A.KITS[ki]} до {A.START_ELO}?",
                     kb([[btn("\u2705 Да, сбросить", "ry", pid, ki), btn("Отмена", "pc", pid)]]), call)
            elif action == "ry":
                pid, ki = int(args[0]), int(args[1])
                ok, res = call_db(lambda conn: A.reset_player_elo(conn, admin, pid, A.KITS[ki]))
                card_screen(chat_id, pid, call, prefix_note=(
                    f"\u2705 {A.KITS[ki]}: {_fmt_elo(res[0])} \u2192 {_fmt_elo(res[1])}" if ok else res))
            elif action == "rg":                       # регион
                pid = int(args[0])
                rows = [[btn(code, "rgs", pid, code) for code in ALLOWED_REGIONS[i:i + 5]]
                        for i in range(0, len(ALLOWED_REGIONS), 5)]
                rows.append([btn("Убрать регион (?)", "rgs", pid, "-")])
                rows.append([btn("\u2B05 Назад", "pc", pid)])
                show(chat_id, "Выберите регион:", kb(rows), call)
            elif action == "rgs":
                pid, code = int(args[0]), args[1]
                region = None if code == "-" else code
                ok, res = call_db(lambda conn: A.set_region(conn, admin, pid, region))
                card_screen(chat_id, pid, call, prefix_note=(
                    f"\u2705 Регион: {res or '?'} \u2192 {region or '?'}" if ok else res))
            elif action == "dv":                       # устройство
                pid, device = int(args[0]), args[1]
                ok, res = call_db(lambda conn: A.set_device(conn, admin, pid, device))
                card_screen(chat_id, pid, call, prefix_note=(
                    f"\u2705 Устройство: {_DEVICE_LABEL.get(res, res)} \u2192 {_DEVICE_LABEL[device]}" if ok else res))
            elif action in ("rm", "rs"):               # скрыть / вернуть
                pid = int(args[0])
                removed = action == "rm"
                ok, res = call_db(lambda conn: A.set_removed(conn, admin, pid, removed))
                card_screen(chat_id, pid, call, prefix_note=(
                    ("\u2705 Игрок скрыт из топа" if removed else "\u2705 Игрок возвращён в топ") if ok else res))
            elif action == "ml":
                matches_screen(chat_id, call)
            elif action == "md":
                match_screen(chat_id, int(args[0]), call)
            elif action == "vq":                       # подтверждение аннулирования
                mid = int(args[0])
                show(chat_id, f"Аннулировать дуэль #{mid}? Обоим игрокам вернётся эло до матча, "
                              f"дуэль исчезнет из истории. Пост в Telegram-топике при этом не удаляется.",
                     kb([[btn("\u2705 Да, аннулировать", "vy", mid), btn("Отмена", "md", mid)]]), call)
            elif action == "vy":
                mid = int(args[0])
                ok, res = call_db(lambda conn: A.void_match(conn, admin, mid))
                show(chat_id, ("\u2705 " + res) if ok else ("\u26A0\uFE0F " + res),
                     kb([[btn("\u2B05 К дуэлям", "ml"), btn("\u2B05 Меню", "menu")]]), call)
            elif action == "st":
                settings_screen(chat_id, call)
            elif action == "sb":
                value = int(args[0])
                ok, res = call_db(lambda conn: A.set_win_bonus(conn, admin, value))
                if ok:
                    settings_screen(chat_id, call)
                else:
                    show(chat_id, res, kb([[btn("\u2B05 Настройки", "st")]]), call)
            elif action == "sg":
                flag = args[0] == "1"
                ok, res = call_db(lambda conn: A.set_tg_results(conn, admin, flag))
                if ok:
                    settings_screen(chat_id, call)
                else:
                    show(chat_id, res, kb([[btn("\u2B05 Настройки", "st")]]), call)
            elif action == "lg":
                log_screen(chat_id, call)
        except Exception as e:  # одно кривое нажатие не должно ронять панель
            print(f"[elo-admin] ошибка обработки {call.data!r}: {e}")
            bot.send_message(chat_id, "Что-то пошло не так, откройте /elo_admin заново.")

    print(f"[elo-admin] панель эло подключена (админов: {len(ids)})")
