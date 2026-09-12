# -*- coding: utf-8 -*-
"""
Панель администратора бота: управление players.js прямо из ЛС с ботом,
через пошаговые inline-кнопки, без необходимости лезть в файл руками.

Доступ ограничен списком Telegram user_id в ADMIN_IDS (см. ниже) - любой
другой пользователь, даже если напишет боту в ЛС, получит отказ.

Поддерживаемые действия (все - через кнопки, без ввода текстовых команд,
кроме случаев, где текст неизбежен - новое имя, новый регион):
  - Изменить тир игрока на ките
  - Переименовать игрока
  - Удалить игрока
  - Сменить регион
  - Поставить/снять Retired на ките

Архитектура:
  - Всё состояние диалога (кто, на каком шаге, что уже выбрано) живёт в
    памяти процесса в словаре _sessions, ключ - user_id. Это МЕЖДУ
    сообщениями одного админа, не персистентно - если бот перезапустится
    посреди диалога, админ просто начинает заново командой /admin.
  - Любое изменение базы идёт через github_storage.update_players_file -
    тот же безопасный механизм с retry на sha-конфликт, что использует
    основной поток бота при обработке результатов тестов. Это отдельный
    вызов, НЕ через result_queue - действия админа синхронные и редкие,
    не нужно ставить их в очередь с результатами тестов.
  - Список игроков для выбора берётся заново с GitHub при каждом входе в
    /admin (не кэшируется), чтобы админ всегда видел актуальное состояние
    базы, даже если бот только что обработал чей-то результат.

Подключение в main.py:
    import admin_panel
    admin_panel.register(bot, GH_REPO, GH_TOKEN)
"""

import telebot
from telebot import types

import github_storage
from bot_config import TIER_ORDER, RETIRED_ELIGIBLE_TIERS


# ==========================================
# ДОСТУП
# ==========================================

# Telegram user_id тех, кому разрешена админ-панель. Добавить сюда ещё
# один ID - значит дать доступ ещё одному человеку; отдельного файла с
# правами специально не заводим, ради простоты - это редко меняется.
ADMIN_IDS = {
    7762233951,  # zor1kkqwix
}

# Список китов, известных базе - используется для клавиатуры выбора кита.
# Если в будущем появится новый кит, добавить его сюда - иначе через
# панель его будет не выбрать (сами данные о новом ките всё равно
# создаются автоматически, если игрок уже проходил по нему тест).
KNOWN_KITS = [
    "Hardcore", "SMP", "Emerald Pot", "Combo", "RVM", "Pickaxe",
    "Emerald", "Diamond Pot", "Dragonhide", "Beast", "Crystal",
    "Mace", "Gapple",
]

# Тиры, доступные для назначения через панель - используем тот же
# TIER_ORDER, что и весь остальной бот (единый источник истины).
ALL_TIERS = list(TIER_ORDER)

_PAGE_SIZE = 8  # сколько игроков показывать на одной "странице" списка

_CALLBACK_DATA_LIMIT = 64  # жёсткий лимит Telegram на длину callback_data в байтах


def _safe_callback(data: str) -> str:
    """
    Telegram молча обрежет callback_data длиннее 64 байт, что незаметно
    сломает кнопку (нажатие ничего не сделает или сделает не то). Лучше
    упасть явно при регистрации кнопки, чем поймать тихий баг в проде -
    это означает, что для конкретного игрока/кита нужно будет укоротить
    схему callback_data (редкий случай, у обычных ников такого не бывает).
    """
    if len(data.encode('utf-8')) > _CALLBACK_DATA_LIMIT:
        raise ValueError(
            f"callback_data превышает {_CALLBACK_DATA_LIMIT} байт ({len(data.encode('utf-8'))}): {data!r}"
        )
    return data


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ==========================================
# СОСТОЯНИЕ ДИАЛОГА (в памяти процесса, на время сессии)
# ==========================================

# session = {
#   'action': 'set_tier' | 'rename' | 'delete' | 'set_region' | 'toggle_retired',
#   'player_name': str | None,
#   'kit': str | None,
#   'page': int,
# }
_sessions = {}


def _get_session(user_id):
    if user_id not in _sessions:
        _sessions[user_id] = {'action': None, 'player_name': None, 'kit': None, 'page': 0}
    return _sessions[user_id]


def _reset_session(user_id):
    _sessions[user_id] = {'action': None, 'player_name': None, 'kit': None, 'page': 0}


# ==========================================
# РАБОТА С ДАННЫМИ (чтение списка игроков для клавиатур)
# ==========================================

def _fetch_players(gh_repo, gh_token):
    """Читает players.js напрямую (без мутации) - для построения клавиатур."""
    players_list, _sha, _prefix, _suffix = github_storage._get_file(gh_repo, gh_token)
    return players_list


def _find_player(players_list, name):
    for p in players_list:
        if p.get('name') == name:
            return p
    return None


# ==========================================
# ПОСТРОЕНИЕ КЛАВИАТУР
# ==========================================

def _main_menu_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🎯 Изменить тир", callback_data="admin:action:set_tier"),
        types.InlineKeyboardButton("✏️ Переименовать игрока", callback_data="admin:action:rename"),
        types.InlineKeyboardButton("🌍 Сменить регион", callback_data="admin:action:set_region"),
        types.InlineKeyboardButton("🧊 Retired (вкл/выкл)", callback_data="admin:action:toggle_retired"),
        types.InlineKeyboardButton("🗑 Удалить игрока", callback_data="admin:action:delete"),
    )
    return kb


def _players_keyboard(players_list, page, action, search=None):
    """
    Клавиатура выбора игрока с пагинацией. action передаётся в
    callback_data, чтобы после выбора игрока знать, какой шаг дальше.
    """
    names = sorted(p.get('name', '?') for p in players_list)
    if search:
        search_lower = search.lower()
        names = [n for n in names if search_lower in n.lower()]

    total_pages = max(1, (len(names) + _PAGE_SIZE - 1) // _PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    start = page * _PAGE_SIZE
    page_names = names[start:start + _PAGE_SIZE]

    kb = types.InlineKeyboardMarkup(row_width=2)
    for name in page_names:
        kb.add(types.InlineKeyboardButton(name, callback_data=f"admin:player:{action}:{name}"))

    nav_row = []
    if page > 0:
        nav_row.append(types.InlineKeyboardButton("⬅️", callback_data=f"admin:page:{action}:{page - 1}"))
    nav_row.append(types.InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="admin:noop"))
    if page < total_pages - 1:
        nav_row.append(types.InlineKeyboardButton("➡️", callback_data=f"admin:page:{action}:{page + 1}"))
    kb.row(*nav_row)

    kb.add(types.InlineKeyboardButton("🔍 Поиск по имени", callback_data=f"admin:search:{action}"))
    kb.add(types.InlineKeyboardButton("« Назад в меню", callback_data="admin:menu"))
    return kb


def _kits_keyboard(action, player_name):
    kb = types.InlineKeyboardMarkup(row_width=2)
    for kit in KNOWN_KITS:
        kb.add(types.InlineKeyboardButton(kit, callback_data=f"admin:kit:{action}:{player_name}:{kit}"))
    kb.add(types.InlineKeyboardButton("« Назад", callback_data="admin:menu"))
    return kb


def _tiers_keyboard(player_name, kit):
    kb = types.InlineKeyboardMarkup(row_width=3)
    buttons = [
        types.InlineKeyboardButton(tier, callback_data=_safe_callback(f"admin:tier:{player_name}:{kit}:{tier}"))
        for tier in ALL_TIERS
    ]
    kb.add(*buttons)
    kb.add(types.InlineKeyboardButton("Unranked (убрать тир)", callback_data=_safe_callback(f"admin:tier:{player_name}:{kit}:Unranked")))
    kb.add(types.InlineKeyboardButton("« Назад", callback_data="admin:menu"))
    return kb


def _confirm_keyboard(yes_callback, no_callback="admin:menu"):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("✅ Подтвердить", callback_data=yes_callback),
        types.InlineKeyboardButton("❌ Отмена", callback_data=no_callback),
    )
    return kb


# ==========================================
# РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ
# ==========================================

def register(bot: telebot.TeleBot, gh_repo: str, gh_token: str):
    """
    Подключает все хендлеры админ-панели к уже созданному экземпляру
    бота. Вызывать один раз при старте main.py, например:

        import admin_panel
        admin_panel.register(bot, GH_REPO, GH_TOKEN)
    """

    def _is_private_admin_message(message):
        return message.chat.type == 'private' and is_admin(message.from_user.id)

    # -------------------- Вход в панель --------------------

    @bot.message_handler(commands=['admin'], func=lambda m: m.chat.type == 'private')
    def cmd_admin(message):
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "⛔ У вас нет доступа к этой команде.")
            return
        _reset_session(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "🛠 <b>Панель администратора MultiCraftCISTiers</b>\n\nВыберите действие:",
            reply_markup=_main_menu_keyboard(),
            parse_mode='HTML',
        )

    # -------------------- Обработка нажатий на inline-кнопки --------------------

    @bot.callback_query_handler(func=lambda c: c.data.startswith('admin:'))
    def handle_admin_callback(call):
        user_id = call.from_user.id
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "⛔ Нет доступа", show_alert=True)
            return

        bot.answer_callback_query(call.id)
        parts = call.data.split(':')
        # parts[0] == 'admin'

        if call.data == 'admin:menu':
            _reset_session(user_id)
            bot.edit_message_text(
                "🛠 <b>Панель администратора MultiCraftCISTiers</b>\n\nВыберите действие:",
                call.message.chat.id, call.message.message_id,
                reply_markup=_main_menu_keyboard(), parse_mode='HTML',
            )
            return

        if call.data == 'admin:noop':
            return

        action_kind = parts[1]

        # ---- Выбор действия из главного меню ----
        if action_kind == 'action':
            action = parts[2]
            session = _get_session(user_id)
            session['action'] = action
            session['page'] = 0

            players_list = _fetch_players(gh_repo, gh_token)
            label = {
                'set_tier': "Изменить тир — выберите игрока:",
                'rename': "Переименовать — выберите игрока:",
                'set_region': "Сменить регион — выберите игрока:",
                'toggle_retired': "Retired — выберите игрока:",
                'delete': "Удалить — выберите игрока:",
            }.get(action, "Выберите игрока:")

            bot.edit_message_text(
                label, call.message.chat.id, call.message.message_id,
                reply_markup=_players_keyboard(players_list, 0, action),
            )
            return

        # ---- Листание страниц списка игроков ----
        if action_kind == 'page':
            action, page_str = parts[2], parts[3]
            page = int(page_str)
            session = _get_session(user_id)
            session['page'] = page

            players_list = _fetch_players(gh_repo, gh_token)
            bot.edit_message_reply_markup(
                call.message.chat.id, call.message.message_id,
                reply_markup=_players_keyboard(players_list, page, action),
            )
            return

        # ---- Запрос текстового поиска по имени ----
        if action_kind == 'search':
            action = parts[2]
            session = _get_session(user_id)
            session['action'] = action
            session['awaiting_search'] = True
            msg = bot.edit_message_text(
                "🔍 Отправьте часть имени игрока для поиска:",
                call.message.chat.id, call.message.message_id,
            )
            bot.register_next_step_handler(msg, _handle_search_input, gh_repo, gh_token, action)
            return

        # ---- Выбор игрока -> следующий шаг зависит от action ----
        if action_kind == 'player':
            action, player_name = parts[2], ':'.join(parts[3:])
            session = _get_session(user_id)
            session['player_name'] = player_name
            session['action'] = action

            if action == 'set_tier':
                bot.edit_message_text(
                    f"Игрок: <b>{player_name}</b>\nВыберите кит:",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=_kits_keyboard('set_tier', player_name), parse_mode='HTML',
                )

            elif action == 'toggle_retired':
                bot.edit_message_text(
                    f"Игрок: <b>{player_name}</b>\nВыберите кит:",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=_kits_keyboard('toggle_retired', player_name), parse_mode='HTML',
                )

            elif action == 'rename':
                msg = bot.edit_message_text(
                    f"Игрок: <b>{player_name}</b>\nОтправьте новое имя:",
                    call.message.chat.id, call.message.message_id, parse_mode='HTML',
                )
                bot.register_next_step_handler(msg, _handle_rename_input, gh_repo, gh_token, player_name)

            elif action == 'set_region':
                msg = bot.edit_message_text(
                    f"Игрок: <b>{player_name}</b>\nОтправьте новый регион (например RU, UA, BY, KZ):",
                    call.message.chat.id, call.message.message_id, parse_mode='HTML',
                )
                bot.register_next_step_handler(msg, _handle_region_input, gh_repo, gh_token, player_name)

            elif action == 'delete':
                bot.edit_message_text(
                    f"⚠️ Удалить игрока <b>{player_name}</b> полностью, вместе со всей историей дуэлей?\nЭто необратимо.",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=_confirm_keyboard(f"admin:confirm_delete:{player_name}"),
                    parse_mode='HTML',
                )
            return

        # ---- Выбор кита (для set_tier / toggle_retired) ----
        if action_kind == 'kit':
            action, player_name, kit = parts[2], parts[3], ':'.join(parts[4:])

            if action == 'set_tier':
                try:
                    kb = _tiers_keyboard(player_name, kit)
                except ValueError:
                    bot.edit_message_text(
                        f"⚠️ Имя игрока «{player_name}» или кит «{kit}» слишком длинные для этого меню. "
                        f"Обратитесь к разработчику для укорачивания схемы кнопок.",
                        call.message.chat.id, call.message.message_id,
                        reply_markup=_main_menu_keyboard(),
                    )
                    return
                bot.edit_message_text(
                    f"Игрок: <b>{player_name}</b>\nКит: <b>{kit}</b>\nВыберите новый тир:",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=kb, parse_mode='HTML',
                )

            elif action == 'toggle_retired':
                players_list = _fetch_players(gh_repo, gh_token)
                player = _find_player(players_list, player_name)
                current = bool(player['tiers'].get(kit, {}).get('retired')) if player and kit in player.get('tiers', {}) else False
                current_tier = player['tiers'].get(kit, {}).get('tier') if player else None

                if not player or kit not in player.get('tiers', {}):
                    bot.edit_message_text(
                        f"⚠️ У игрока {player_name} нет данных по киту {kit} - нечего переключать.",
                        call.message.chat.id, call.message.message_id,
                        reply_markup=_main_menu_keyboard(),
                    )
                    return

                if current_tier not in RETIRED_ELIGIBLE_TIERS:
                    bot.edit_message_text(
                        f"⚠️ Тир {current_tier} на ките {kit} не входит в диапазон, для которого "
                        f"предусмотрен статус Retired ({', '.join(RETIRED_ELIGIBLE_TIERS)}).\n"
                        f"Изменение не применено.",
                        call.message.chat.id, call.message.message_id,
                        reply_markup=_main_menu_keyboard(),
                    )
                    return

                new_value = not current
                ok = _apply_mutation(
                    gh_repo, gh_token,
                    lambda players_list, pn=player_name, k=kit, v=new_value: _mutate_toggle_retired(players_list, pn, k, v),
                    f"Админ-панель: {'установлен' if new_value else 'снят'} Retired у {player_name} / {kit}",
                    bot=bot, chat_id=call.message.chat.id, message_id=call.message.message_id,
                )
                if not ok:
                    return
                status = "теперь Retired ✅" if new_value else "больше не Retired"
                bot.edit_message_text(
                    f"Готово. {player_name} / {kit} {status}.",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=_main_menu_keyboard(),
                )
            return

        # ---- Выбор нового тира (финальный шаг set_tier) ----
        if action_kind == 'tier':
            player_name, kit, tier = parts[2], parts[3], ':'.join(parts[4:])
            bot.edit_message_text(
                f"Установить <b>{player_name}</b> / <b>{kit}</b> → <b>{tier}</b>?",
                call.message.chat.id, call.message.message_id,
                reply_markup=_confirm_keyboard(f"admin:confirm_tier:{player_name}:{kit}:{tier}"),
                parse_mode='HTML',
            )
            return

        # ---- Подтверждение установки тира ----
        if action_kind == 'confirm_tier':
            player_name, kit, tier = parts[2], parts[3], ':'.join(parts[4:])
            ok = _apply_mutation(
                gh_repo, gh_token,
                lambda players_list, pn=player_name, k=kit, t=tier: _mutate_set_tier(players_list, pn, k, t),
                f"Админ-панель: установлен тир {tier} у {player_name} / {kit}",
                bot=bot, chat_id=call.message.chat.id, message_id=call.message.message_id,
            )
            if not ok:
                return
            bot.edit_message_text(
                f"✅ Готово. {player_name} / {kit} → {tier}.",
                call.message.chat.id, call.message.message_id,
                reply_markup=_main_menu_keyboard(),
            )
            return

        # ---- Подтверждение удаления игрока ----
        if action_kind == 'confirm_delete':
            player_name = ':'.join(parts[2:])
            ok = _apply_mutation(
                gh_repo, gh_token,
                lambda players_list, pn=player_name: _mutate_delete_player(players_list, pn),
                f"Админ-панель: удалён игрок {player_name}",
                bot=bot, chat_id=call.message.chat.id, message_id=call.message.message_id,
            )
            if not ok:
                return
            bot.edit_message_text(
                f"🗑 Игрок {player_name} удалён.",
                call.message.chat.id, call.message.message_id,
                reply_markup=_main_menu_keyboard(),
            )
            return

    # -------------------- Текстовый ввод (поиск / новое имя / новый регион) --------------------

    def _handle_search_input(message, gh_repo, gh_token, action):
        if not is_admin(message.from_user.id):
            return
        search = message.text.strip()
        players_list = _fetch_players(gh_repo, gh_token)
        bot.send_message(
            message.chat.id,
            f"Результаты поиска по «{search}»:",
            reply_markup=_players_keyboard(players_list, 0, action, search=search),
        )

    def _handle_rename_input(message, gh_repo, gh_token, old_name):
        if not is_admin(message.from_user.id):
            return
        new_name = message.text.strip()
        if not new_name:
            bot.send_message(message.chat.id, "⚠️ Имя не может быть пустым. Повторите /admin.")
            return
        bot.send_message(
            message.chat.id,
            f"Переименовать <b>{old_name}</b> → <b>{new_name}</b>?",
            reply_markup=_confirm_keyboard(f"admin:confirm_rename:{old_name}:{new_name}"),
            parse_mode='HTML',
        )

    def _handle_region_input(message, gh_repo, gh_token, player_name):
        if not is_admin(message.from_user.id):
            return
        new_region = message.text.strip().upper()
        bot.send_message(
            message.chat.id,
            f"Установить регион <b>{player_name}</b> → <b>{new_region}</b>?",
            reply_markup=_confirm_keyboard(f"admin:confirm_region:{player_name}:{new_region}"),
            parse_mode='HTML',
        )

    # Отдельные callback-и для подтверждения rename/region (не вписались в
    # общий handle_admin_callback выше по порядку регистрации - telebot
    # поддерживает несколько callback_query_handler, срабатывает первый
    # подходящий по filter'у, поэтому здесь сужаем через startswith).

    @bot.callback_query_handler(func=lambda c: c.data.startswith('admin:confirm_rename:'))
    def handle_confirm_rename(call):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "⛔ Нет доступа", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        _, _, old_name, new_name = call.data.split(':', 3)
        ok = _apply_mutation(
            gh_repo, gh_token,
            lambda players_list, o=old_name, n=new_name: _mutate_rename_player(players_list, o, n),
            f"Админ-панель: переименован {old_name} -> {new_name}",
            bot=bot, chat_id=call.message.chat.id, message_id=call.message.message_id,
        )
        if not ok:
            return
        bot.edit_message_text(
            f"✅ Готово. {old_name} переименован в {new_name}.",
            call.message.chat.id, call.message.message_id,
            reply_markup=_main_menu_keyboard(),
        )

    @bot.callback_query_handler(func=lambda c: c.data.startswith('admin:confirm_region:'))
    def handle_confirm_region(call):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "⛔ Нет доступа", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        _, _, player_name, new_region = call.data.split(':', 3)
        ok = _apply_mutation(
            gh_repo, gh_token,
            lambda players_list, pn=player_name, r=new_region: _mutate_set_region(players_list, pn, r),
            f"Админ-панель: регион {player_name} -> {new_region}",
            bot=bot, chat_id=call.message.chat.id, message_id=call.message.message_id,
        )
        if not ok:
            return
        bot.edit_message_text(
            f"✅ Готово. Регион {player_name} → {new_region}.",
            call.message.chat.id, call.message.message_id,
            reply_markup=_main_menu_keyboard(),
        )


# ==========================================
# ФУНКЦИИ-МУТАТОРЫ (передаются в github_storage.update_players_file)
# ==========================================

def _apply_mutation(gh_repo, gh_token, mutate_fn, commit_message, bot=None, chat_id=None, message_id=None):
    """
    Обёртка вокруг update_players_file с единообразной обработкой ошибок.
    Если переданы bot/chat_id/message_id и мутация падает (игрок не
    найден, сбой сети/GitHub) - редактирует сообщение с понятным текстом
    ошибки вместо того, чтобы уронить весь callback-обработчик молча.
    Возвращает True при успехе, False при ошибке.
    """
    try:
        github_storage.update_players_file(gh_repo, gh_token, mutate_fn, commit_message)
        return True
    except (github_storage.GithubStorageError, RuntimeError) as e:
        if bot is not None and chat_id is not None and message_id is not None:
            bot.edit_message_text(
                f"⚠️ Не удалось применить изменение: {e}",
                chat_id, message_id,
                reply_markup=_main_menu_keyboard(),
            )
        return False


def _mutate_set_tier(players_list, player_name, kit, tier):
    from tier_logic import today_str
    player = _find_player(players_list, player_name)
    if not player:
        raise RuntimeError(f"Игрок {player_name} не найден")
    if tier == "Unranked":
        player.get('tiers', {}).pop(kit, None)
    else:
        player.setdefault('tiers', {})[kit] = {
            "tier": tier,
            "date": today_str(),
            "retired": False,
        }
    return players_list


def _mutate_toggle_retired(players_list, player_name, kit, new_value):
    player = _find_player(players_list, player_name)
    if not player or kit not in player.get('tiers', {}):
        raise RuntimeError(f"Нет данных {player_name}/{kit}")
    player['tiers'][kit]['retired'] = new_value
    return players_list


def _mutate_rename_player(players_list, old_name, new_name):
    player = _find_player(players_list, old_name)
    if not player:
        raise RuntimeError(f"Игрок {old_name} не найден")
    player['name'] = new_name

    # Переименовываем упоминания и в чужих matchHistory (opponent/tester)
    for p in players_list:
        for entry in p.get('matchHistory', []):
            if entry.get('opponent') == old_name:
                entry['opponent'] = new_name
            if entry.get('tester') == old_name:
                entry['tester'] = new_name
    return players_list


def _mutate_set_region(players_list, player_name, region):
    player = _find_player(players_list, player_name)
    if not player:
        raise RuntimeError(f"Игрок {player_name} не найден")
    player['region'] = region
    return players_list


def _mutate_delete_player(players_list, player_name):
    return [p for p in players_list if p.get('name') != player_name]
