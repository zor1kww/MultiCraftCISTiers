# -*- coding: utf-8 -*-
"""
Панель администратора бота: управление players.js прямо из ЛС с ботом,
через пошаговые inline-кнопки, без необходимости лезть в файл руками.

Доступ ограничен списком Telegram user_id в ADMIN_IDS (см. ниже) - любой
другой пользователь, даже если напишет боту в ЛС, получит отказ.

Поддерживаемые действия (все - через кнопки, без ввода текстовых команд,
кроме случаев, где текст неизбежен - новое имя, новый регион, точное
число штрафных очков):
  - Изменить тир игрока на ките
  - Переименовать игрока
  - Удалить игрока
  - Сменить регион
  - Поставить/снять Retired на ките
  - Заморозить/разморозить ВСЕ HT1-HT3 киты игрока разом (одной кнопкой)
  - Штрафные очки на ките: +0.5 / -0.5 или точное число, с тем же
    авто-понижением при достижении PENALTY_DEMOTION_THRESHOLD, что и при
    обычном начислении штрафа за тест
  - Просмотр/редактирование/удаление конкретной записи в логе дуэлей
    игрока (поиск по киту и дате из его собственной matchHistory)

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
  - Штрафная логика переиспользует penalty_logic.add_penalty_to_entry и
    penalty_logic.next_tier_down - те же функции, что использует основной
    поток бота при обычном начислении штрафа за тест, чтобы поведение не
    расходилось между "штраф за тест" и "штраф вручную через панель".

Подключение в main.py:
    import admin_panel
    admin_panel.register(bot, GH_REPO, GH_TOKEN)
"""

import functools
import re

import telebot
from telebot import types

import github_storage
from bot_config import TIER_ORDER, RETIRED_ELIGIBLE_TIERS, PENALTY_DEMOTION_THRESHOLD
from penalty_logic import add_penalty_to_entry, next_tier_down
from tier_logic import today_str



# ------------------------------------------------------------------
# Кодирование имён в callback_data.
# Лимит Telegram - 64 БАЙТА, а кириллица весит 2 байта/символ, плюс
# двоеточие в нике ломает разбор по ':'. Поэтому длинные/«опасные» имена
# заменяются коротким токеном ~xxxxxxxx (хранится в памяти процесса),
# а при разборе callback_data токены раскрываются обратно в имена.
# ------------------------------------------------------------------
import hashlib
import html as _html

_NAME_TOKENS = {}   # token -> real name
_TOKEN_RE = re.compile(r'^~[0-9a-f]{8}$')
_INLINE_NAME_MAX_BYTES = 14


def _enc(name: str) -> str:
    name = str(name)
    if (':' not in name and '~' not in name
            and len(name.encode('utf-8')) <= _INLINE_NAME_MAX_BYTES):
        return name
    token = '~' + hashlib.sha1(name.encode('utf-8')).hexdigest()[:8]
    _NAME_TOKENS[token] = name
    return token


class _StaleToken(Exception):
    pass


def _dec(part: str) -> str:
    if _TOKEN_RE.match(part):
        if part not in _NAME_TOKENS:
            raise _StaleToken(part)
        return _NAME_TOKENS[part]
    return part


def _split(data: str, maxsplit: int = -1):
    """split(':') + раскрытие токенов имён. Токены не содержат ':', поэтому
    разбор безопасен даже для ников с двоеточием."""
    return [_dec(p) for p in data.split(':', maxsplit)]


def _esc(text) -> str:
    """Экранирование для parse_mode='HTML' (ники/комментарии могут содержать < > &)."""
    return _html.escape(str(text), quote=False)


def _input_text(bot, message):
    """Текст шага ввода или None. Команды (/admin) и нетекстовые сообщения
    отменяют шаг, а не принимаются как имя/регион/число."""
    text = getattr(message, 'text', None)
    if not text or text.strip().startswith('/'):
        bot.send_message(message.chat.id, "Ввод отменён. Откройте /admin, чтобы начать заново.")
        return None
    return text.strip()


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


def _eligible_kits_for_freeze(player):
    """
    Возвращает список (kit, tier) для китов игрока, чей тир входит в
    RETIRED_ELIGIBLE_TIERS (HT1-HT3) - именно эти киты можно
    заморозить/разморозить массово одной кнопкой. Киты ниже HT3 не
    поддерживают Retired на сайте (см. parseTierInfo во фронтенде) и
    сюда не попадают.
    """
    result = []
    for kit, data in player.get('tiers', {}).items():
        if data.get('tier') in RETIRED_ELIGIBLE_TIERS:
            result.append((kit, data.get('tier')))
    return result


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
        types.InlineKeyboardButton("❄️ Заморозить все HT1-HT3", callback_data="admin:action:freeze_all"),
        types.InlineKeyboardButton("🔥 Разморозить все HT1-HT3", callback_data="admin:action:unfreeze_all"),
        types.InlineKeyboardButton("⚠️ Штрафные очки", callback_data="admin:action:penalty"),
        types.InlineKeyboardButton("📜 Лог дуэлей", callback_data="admin:action:duel_log"),
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
        kb.add(types.InlineKeyboardButton(name, callback_data=f"admin:player:{action}:{_enc(name)}"))

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
        kb.add(types.InlineKeyboardButton(kit, callback_data=_safe_callback(f"admin:kit:{action}:{_enc(player_name)}:{kit}")))
    kb.add(types.InlineKeyboardButton("« Назад", callback_data="admin:menu"))
    return kb


def _tiers_keyboard(player_name, kit):
    kb = types.InlineKeyboardMarkup(row_width=3)
    buttons = [
        types.InlineKeyboardButton(tier, callback_data=_safe_callback(f"admin:tier:{_enc(player_name)}:{kit}:{tier}"))
        for tier in ALL_TIERS
    ]
    kb.add(*buttons)
    kb.add(types.InlineKeyboardButton("Unranked (убрать тир)", callback_data=_safe_callback(f"admin:tier:{_enc(player_name)}:{kit}:Unranked")))
    kb.add(types.InlineKeyboardButton("« Назад", callback_data="admin:menu"))
    return kb


def _confirm_keyboard(yes_callback, no_callback="admin:menu"):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("✅ Подтвердить", callback_data=yes_callback),
        types.InlineKeyboardButton("❌ Отмена", callback_data=no_callback),
    )
    return kb


def _penalty_keyboard(player_name, kit):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("+0.5", callback_data=_safe_callback(f"admin:penaltyadj:{_enc(player_name)}:{kit}:0.5")),
        types.InlineKeyboardButton("-0.5", callback_data=_safe_callback(f"admin:penaltyadj:{_enc(player_name)}:{kit}:-0.5")),
    )
    kb.add(types.InlineKeyboardButton("✏️ Ввести точное число", callback_data=_safe_callback(f"admin:penaltyexact:{_enc(player_name)}:{kit}")))
    kb.add(types.InlineKeyboardButton("« Назад", callback_data="admin:menu"))
    return kb


def _distinct_dates_for_kit(player, kit):
    """Уникальные даты записей matchHistory игрока по конкретному киту,
    отсортированные по убыванию (сначала самые свежие)."""
    dates = sorted({
        entry.get('date') for entry in player.get('matchHistory', [])
        if entry.get('kit') == kit and entry.get('date')
    }, reverse=True)
    return dates


def _dates_keyboard(player_name, kit, dates):
    kb = types.InlineKeyboardMarkup(row_width=2)
    for d in dates[:20]:  # ограничиваем на случай очень длинной истории по киту
        kb.add(types.InlineKeyboardButton(d, callback_data=_safe_callback(f"admin:duelddate:{_enc(player_name)}:{kit}:{d}")))
    kb.add(types.InlineKeyboardButton("« Назад", callback_data="admin:menu"))
    return kb


def _entries_for_kit_and_date(player, kit, date_str):
    """Список (index, entry) записей matchHistory игрока, совпадающих по
    киту и дате - для случаев, когда в один день было несколько дуэлей
    по одному киту (например многодуэльный HT1-тест)."""
    return [
        (i, e) for i, e in enumerate(player.get('matchHistory', []))
        if e.get('kit') == kit and e.get('date') == date_str
    ]


def _duel_entry_summary(entry):
    """Короткое читаемое описание одной записи лога дуэлей для кнопки/сообщения."""
    opponent = entry.get('opponent') or entry.get('tester') or '?'
    score_player = entry.get('scorePlayer', '?')
    score_opponent = entry.get('scoreOpponent', entry.get('scoreTester', '?'))
    return f"vs {opponent} ({score_player}:{score_opponent})"


def _entries_keyboard(player_name, kit, date_str, entries):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for idx, entry in entries:
        kb.add(types.InlineKeyboardButton(
            _duel_entry_summary(entry),
            callback_data=_safe_callback(f"admin:duelpick:{_enc(player_name)}:{kit}:{date_str}:{idx}"),
        ))
    kb.add(types.InlineKeyboardButton("« Назад", callback_data="admin:menu"))
    return kb


def _duel_edit_keyboard(player_name, kit, date_str, idx):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("✏️ Изменить счёт", callback_data=_safe_callback(f"admin:dueleditscore:{_enc(player_name)}:{kit}:{date_str}:{idx}")),
        types.InlineKeyboardButton("✏️ Изменить тир до/после", callback_data=_safe_callback(f"admin:dueledittier:{_enc(player_name)}:{kit}:{date_str}:{idx}")),
        types.InlineKeyboardButton("🗑 Удалить запись", callback_data=_safe_callback(f"admin:dueldelete:{_enc(player_name)}:{kit}:{date_str}:{idx}")),
        types.InlineKeyboardButton("« Назад", callback_data="admin:menu"),
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


    # ВАЖНО про маршрутизацию: pyTelegramBotAPI вызывает ТОЛЬКО ПЕРВЫЙ handler,
    # чей filter вернул True. Раньше общий handler с filter startswith('admin:')
    # перехватывал ВСЕ кнопки, и специализированные handler'ы ниже (rename,
    # region, freeze, штрафы, лог дуэлей) были недостижимы - кнопки молчали.
    # Теперь общий handler берёт только свои виды callback-ов, а остальные
    # фильтры не пересекаются по префиксу.
    _MAIN_KINDS = {'menu', 'noop', 'action', 'page', 'search', 'player', 'kit',
                   'tier', 'confirm_tier', 'confirm_delete'}

    def _kind(c):
        d = c.data or ''
        if not d.startswith('admin:'):
            return None
        return d.split(':', 2)[1]

    def _cbh(flt):
        """callback_query_handler + перехват устаревших кнопок (токен имени
        пропал после рестарта бота) - вместо тихого молчания просим /admin."""
        def deco(fn):
            @functools.wraps(fn)
            def wrapper(call):
                try:
                    return fn(call)
                except _StaleToken:
                    try:
                        bot.answer_callback_query(call.id, "Кнопка устарела - откройте /admin заново", show_alert=True)
                    except Exception:
                        pass
            return bot.callback_query_handler(func=flt)(wrapper)
        return deco

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

    @_cbh(lambda c: _kind(c) in _MAIN_KINDS)
    def handle_admin_callback(call):
        user_id = call.from_user.id
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "⛔ Нет доступа", show_alert=True)
            return

        bot.answer_callback_query(call.id)
        parts = _split(call.data)
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
                'freeze_all': "Заморозить все HT1-HT3 — выберите игрока:",
                'unfreeze_all': "Разморозить все HT1-HT3 — выберите игрока:",
                'penalty': "Штрафные очки — выберите игрока:",
                'duel_log': "Лог дуэлей — выберите игрока:",
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
                    f"Игрок: <b>{_esc(player_name)}</b>\nВыберите кит:",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=_kits_keyboard('set_tier', player_name), parse_mode='HTML',
                )

            elif action == 'toggle_retired':
                bot.edit_message_text(
                    f"Игрок: <b>{_esc(player_name)}</b>\nВыберите кит:",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=_kits_keyboard('toggle_retired', player_name), parse_mode='HTML',
                )

            elif action == 'rename':
                msg = bot.edit_message_text(
                    f"Игрок: <b>{_esc(player_name)}</b>\nОтправьте новое имя:",
                    call.message.chat.id, call.message.message_id, parse_mode='HTML',
                )
                bot.register_next_step_handler(msg, _handle_rename_input, gh_repo, gh_token, player_name)

            elif action == 'set_region':
                msg = bot.edit_message_text(
                    f"Игрок: <b>{_esc(player_name)}</b>\nОтправьте новый регион (например RU, UA, BY, KZ):",
                    call.message.chat.id, call.message.message_id, parse_mode='HTML',
                )
                bot.register_next_step_handler(msg, _handle_region_input, gh_repo, gh_token, player_name)

            elif action == 'delete':
                bot.edit_message_text(
                    f"⚠️ Удалить игрока <b>{_esc(player_name)}</b> полностью, вместе со всей историей дуэлей?\nЭто необратимо.",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=_confirm_keyboard(f"admin:confirm_delete:{_enc(player_name)}"),
                    parse_mode='HTML',
                )

            elif action in ('freeze_all', 'unfreeze_all'):
                players_list = _fetch_players(gh_repo, gh_token)
                player = _find_player(players_list, player_name)
                eligible_kits = _eligible_kits_for_freeze(player) if player else []

                if not eligible_kits:
                    bot.edit_message_text(
                        f"⚠️ У игрока {player_name} нет китов в диапазоне "
                        f"{', '.join(RETIRED_ELIGIBLE_TIERS)} - нечего "
                        f"{'замораживать' if action == 'freeze_all' else 'размораживать'}.",
                        call.message.chat.id, call.message.message_id,
                        reply_markup=_main_menu_keyboard(),
                    )
                    return

                verb = "заморозить" if action == 'freeze_all' else "разморозить"
                kits_list = ", ".join(f"{kit} ({tier})" for kit, tier in eligible_kits)
                bot.edit_message_text(
                    f"{'❄️' if action == 'freeze_all' else '🔥'} {verb.capitalize()} у <b>{_esc(player_name)}</b> "
                    f"следующие киты: {kits_list}?",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=_confirm_keyboard(f"admin:confirm_{action}:{_enc(player_name)}"),
                    parse_mode='HTML',
                )

            elif action == 'penalty':
                bot.edit_message_text(
                    f"Игрок: <b>{_esc(player_name)}</b>\nВыберите кит:",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=_kits_keyboard('penalty', player_name), parse_mode='HTML',
                )

            elif action == 'duel_log':
                bot.edit_message_text(
                    f"Игрок: <b>{_esc(player_name)}</b>\nВыберите кит:",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=_kits_keyboard('duel_log', player_name), parse_mode='HTML',
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
                    f"Игрок: <b>{_esc(player_name)}</b>\nКит: <b>{_esc(kit)}</b>\nВыберите новый тир:",
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

            elif action == 'penalty':
                players_list = _fetch_players(gh_repo, gh_token)
                player = _find_player(players_list, player_name)
                current_points = 0.0
                if player:
                    current_points = player.get('penaltyByKit', {}).get(kit, {}).get('points', 0.0)
                bot.edit_message_text(
                    f"Игрок: <b>{_esc(player_name)}</b>\nКит: <b>{_esc(kit)}</b>\n"
                    f"Текущие штрафные очки: <b>{current_points}</b>\n\n"
                    f"Выберите действие:",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=_penalty_keyboard(player_name, kit), parse_mode='HTML',
                )

            elif action == 'duel_log':
                players_list = _fetch_players(gh_repo, gh_token)
                player = _find_player(players_list, player_name)
                dates = _distinct_dates_for_kit(player, kit) if player else []

                if not dates:
                    bot.edit_message_text(
                        f"⚠️ У игрока {player_name} нет записей в логе дуэлей по киту {kit}.",
                        call.message.chat.id, call.message.message_id,
                        reply_markup=_main_menu_keyboard(),
                    )
                    return

                bot.edit_message_text(
                    f"Игрок: <b>{_esc(player_name)}</b>\nКит: <b>{_esc(kit)}</b>\nВыберите дату записи:",
                    call.message.chat.id, call.message.message_id,
                    reply_markup=_dates_keyboard(player_name, kit, dates), parse_mode='HTML',
                )
            return

        # ---- Выбор нового тира (финальный шаг set_tier) ----
        if action_kind == 'tier':
            player_name, kit, tier = parts[2], parts[3], ':'.join(parts[4:])
            bot.edit_message_text(
                f"Установить <b>{_esc(player_name)}</b> / <b>{_esc(kit)}</b> → <b>{_esc(tier)}</b>?",
                call.message.chat.id, call.message.message_id,
                reply_markup=_confirm_keyboard(f"admin:confirm_tier:{_enc(player_name)}:{kit}:{tier}"),
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
        search = _input_text(bot, message)
        if search is None:
            return
        players_list = _fetch_players(gh_repo, gh_token)
        bot.send_message(
            message.chat.id,
            f"Результаты поиска по «{search}»:",
            reply_markup=_players_keyboard(players_list, 0, action, search=search),
        )

    def _handle_rename_input(message, gh_repo, gh_token, old_name):
        if not is_admin(message.from_user.id):
            return
        new_name = _input_text(bot, message)
        if new_name is None:
            return
        if not new_name:
            bot.send_message(message.chat.id, "⚠️ Имя не может быть пустым. Повторите /admin.")
            return
        bot.send_message(
            message.chat.id,
            f"Переименовать <b>{_esc(old_name)}</b> → <b>{_esc(new_name)}</b>?",
            reply_markup=_confirm_keyboard(_safe_callback(f"admin:confirm_rename:{_enc(old_name)}:{_enc(new_name)}")),
            parse_mode='HTML',
        )

    def _handle_region_input(message, gh_repo, gh_token, player_name):
        if not is_admin(message.from_user.id):
            return
        new_region = _input_text(bot, message)
        if new_region is None:
            return
        new_region = new_region.upper()
        bot.send_message(
            message.chat.id,
            f"Установить регион <b>{_esc(player_name)}</b> → <b>{_esc(new_region)}</b>?",
            reply_markup=_confirm_keyboard(_safe_callback(f"admin:confirm_region:{_enc(player_name)}:{_enc(new_region)}")),
            parse_mode='HTML',
        )

    # Отдельные callback-и для подтверждения rename/region (не вписались в
    # общий handle_admin_callback выше по порядку регистрации - telebot
    # поддерживает несколько callback_query_handler, срабатывает первый
    # подходящий по filter'у, поэтому здесь сужаем через startswith).

    @_cbh(lambda c: (c.data or '').startswith('admin:confirm_rename:'))
    def handle_confirm_rename(call):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "⛔ Нет доступа", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        _, _, old_name, new_name = _split(call.data, 3)
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

    @_cbh(lambda c: (c.data or '').startswith('admin:confirm_region:'))
    def handle_confirm_region(call):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "⛔ Нет доступа", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        _, _, player_name, new_region = _split(call.data, 3)
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

    # -------------------- Заморозка/разморозка всех HT1-HT3 китов разом --------------------

    @_cbh(lambda c: (c.data or '').startswith('admin:confirm_freeze_all:'))
    def handle_confirm_freeze_all(call):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "⛔ Нет доступа", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        player_name = _split(call.data, 2)[2]
        ok = _apply_mutation(
            gh_repo, gh_token,
            lambda players_list, pn=player_name: _mutate_freeze_all(players_list, pn, True),
            f"Админ-панель: заморожены все HT1-HT3 киты у {player_name}",
            bot=bot, chat_id=call.message.chat.id, message_id=call.message.message_id,
        )
        if not ok:
            return
        bot.edit_message_text(
            f"❄️ Готово. У {player_name} заморожены все киты в диапазоне {', '.join(RETIRED_ELIGIBLE_TIERS)}.",
            call.message.chat.id, call.message.message_id,
            reply_markup=_main_menu_keyboard(),
        )

    @_cbh(lambda c: (c.data or '').startswith('admin:confirm_unfreeze_all:'))
    def handle_confirm_unfreeze_all(call):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "⛔ Нет доступа", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        player_name = _split(call.data, 2)[2]
        ok = _apply_mutation(
            gh_repo, gh_token,
            lambda players_list, pn=player_name: _mutate_freeze_all(players_list, pn, False),
            f"Админ-панель: разморожены все HT1-HT3 киты у {player_name}",
            bot=bot, chat_id=call.message.chat.id, message_id=call.message.message_id,
        )
        if not ok:
            return
        bot.edit_message_text(
            f"🔥 Готово. У {player_name} сняты Retired со всех китов в диапазоне {', '.join(RETIRED_ELIGIBLE_TIERS)}.",
            call.message.chat.id, call.message.message_id,
            reply_markup=_main_menu_keyboard(),
        )

    # -------------------- Штрафные очки --------------------

    @_cbh(lambda c: (c.data or '').startswith('admin:penaltyadj:'))
    def handle_penalty_adjust(call):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "⛔ Нет доступа", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        _, _, player_name, kit, delta_str = _split(call.data, 4)
        delta = float(delta_str)
        _apply_penalty_change(bot, gh_repo, gh_token, call.message.chat.id, call.message.message_id, player_name, kit, delta)

    @_cbh(lambda c: (c.data or '').startswith('admin:penaltyexact:'))
    def handle_penalty_exact_request(call):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "⛔ Нет доступа", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        _, _, player_name, kit = _split(call.data, 3)
        msg = bot.edit_message_text(
            f"Игрок: <b>{_esc(player_name)}</b>\nКит: <b>{_esc(kit)}</b>\n"
            f"Отправьте новое значение штрафных очков (например 1.5):",
            call.message.chat.id, call.message.message_id, parse_mode='HTML',
        )
        bot.register_next_step_handler(msg, _handle_penalty_exact_input, gh_repo, gh_token, player_name, kit)

    def _handle_penalty_exact_input(message, gh_repo, gh_token, player_name, kit):
        if not is_admin(message.from_user.id):
            return
        raw = _input_text(bot, message)
        if raw is None:
            return
        try:
            new_value = float(raw.replace(',', '.'))
        except ValueError:
            bot.send_message(message.chat.id, "⚠️ Не удалось распознать число. Повторите /admin.")
            return
        _apply_penalty_set(bot, gh_repo, gh_token, message.chat.id, None, player_name, kit, new_value)

    # -------------------- Лог дуэлей: выбор даты / записи --------------------

    @_cbh(lambda c: (c.data or '').startswith('admin:duelddate:'))
    def handle_duel_date(call):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "⛔ Нет доступа", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        _, _, player_name, kit, date_str = _split(call.data, 4)

        players_list = _fetch_players(gh_repo, gh_token)
        player = _find_player(players_list, player_name)
        entries = _entries_for_kit_and_date(player, kit, date_str) if player else []

        if not entries:
            bot.edit_message_text(
                "⚠️ Записи не найдены (возможно, база изменилась). Начните заново через /admin.",
                call.message.chat.id, call.message.message_id,
                reply_markup=_main_menu_keyboard(),
            )
            return

        if len(entries) == 1:
            idx, entry = entries[0]
            bot.edit_message_text(
                _format_duel_entry(player_name, kit, date_str, entry),
                call.message.chat.id, call.message.message_id,
                reply_markup=_duel_edit_keyboard(player_name, kit, date_str, idx), parse_mode='HTML',
            )
        else:
            bot.edit_message_text(
                f"Найдено {len(entries)} записей за {date_str}. Выберите нужную:",
                call.message.chat.id, call.message.message_id,
                reply_markup=_entries_keyboard(player_name, kit, date_str, entries),
            )

    @_cbh(lambda c: (c.data or '').startswith('admin:duelpick:'))
    def handle_duel_pick(call):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "⛔ Нет доступа", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        _, _, player_name, kit, date_str, idx_str = _split(call.data, 5)
        idx = int(idx_str)

        players_list = _fetch_players(gh_repo, gh_token)
        player = _find_player(players_list, player_name)
        entry = player['matchHistory'][idx] if player and idx < len(player.get('matchHistory', [])) else None

        if not entry:
            bot.edit_message_text(
                "⚠️ Запись не найдена (возможно, база изменилась). Начните заново через /admin.",
                call.message.chat.id, call.message.message_id,
                reply_markup=_main_menu_keyboard(),
            )
            return

        bot.edit_message_text(
            _format_duel_entry(player_name, kit, date_str, entry),
            call.message.chat.id, call.message.message_id,
            reply_markup=_duel_edit_keyboard(player_name, kit, date_str, idx), parse_mode='HTML',
        )

    # -------------------- Лог дуэлей: удаление записи --------------------

    @_cbh(lambda c: (c.data or '').startswith('admin:dueldelete:'))
    def handle_duel_delete(call):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "⛔ Нет доступа", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        _, _, player_name, kit, date_str, idx_str = _split(call.data, 5)
        try:
            confirm_data = _safe_callback(f"admin:confirm_dueldelete:{_enc(player_name)}:{kit}:{date_str}:{idx_str}")
        except ValueError:
            bot.edit_message_text(
                "⚠️ Слишком длинное имя игрока/кита для этого меню. Обратитесь к разработчику.",
                call.message.chat.id, call.message.message_id,
                reply_markup=_main_menu_keyboard(),
            )
            return
        bot.edit_message_text(
            f"⚠️ Удалить эту запись из лога дуэлей {player_name} безвозвратно?",
            call.message.chat.id, call.message.message_id,
            reply_markup=_confirm_keyboard(confirm_data),
        )

    @_cbh(lambda c: (c.data or '').startswith('admin:confirm_dueldelete:'))
    def handle_confirm_duel_delete(call):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "⛔ Нет доступа", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        _, _, player_name, kit, date_str, idx_str = _split(call.data, 5)
        idx = int(idx_str)
        ok = _apply_mutation(
            gh_repo, gh_token,
            lambda players_list, pn=player_name, i=idx: _mutate_delete_duel_entry(players_list, pn, i),
            f"Админ-панель: удалена запись лога дуэлей у {player_name} ({kit}, {date_str})",
            bot=bot, chat_id=call.message.chat.id, message_id=call.message.message_id,
        )
        if not ok:
            return
        bot.edit_message_text(
            f"🗑 Запись удалена из лога дуэлей {player_name}.",
            call.message.chat.id, call.message.message_id,
            reply_markup=_main_menu_keyboard(),
        )

    # -------------------- Лог дуэлей: изменение счёта --------------------

    @_cbh(lambda c: (c.data or '').startswith('admin:dueleditscore:'))
    def handle_duel_edit_score_request(call):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "⛔ Нет доступа", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        _, _, player_name, kit, date_str, idx_str = _split(call.data, 5)
        msg = bot.edit_message_text(
            f"Игрок: <b>{_esc(player_name)}</b>\nОтправьте новый счёт в формате <code>4:2</code> "
            f"(сначала счёт {_esc(player_name)}, потом счёт оппонента):",
            call.message.chat.id, call.message.message_id, parse_mode='HTML',
        )
        bot.register_next_step_handler(msg, _handle_duel_score_input, gh_repo, gh_token, player_name, kit, date_str, int(idx_str))

    def _handle_duel_score_input(message, gh_repo, gh_token, player_name, kit, date_str, idx):
        if not is_admin(message.from_user.id):
            return
        text = _input_text(bot, message)
        if text is None:
            return
        if ':' not in text:
            bot.send_message(message.chat.id, "⚠️ Формат должен быть «4:2». Повторите /admin.")
            return
        left, right = text.split(':', 1)
        try:
            score_player, score_opponent = int(left.strip()), int(right.strip())
        except ValueError:
            bot.send_message(message.chat.id, "⚠️ Не удалось распознать числа. Повторите /admin.")
            return

        ok = _apply_mutation(
            gh_repo, gh_token,
            lambda players_list, pn=player_name, i=idx, sp=score_player, so=score_opponent: _mutate_edit_duel_score(players_list, pn, i, sp, so),
            f"Админ-панель: изменён счёт в записи лога дуэлей {player_name} ({kit}, {date_str})",
            bot=bot, chat_id=message.chat.id, message_id=None,
        )
        if not ok:
            bot.send_message(message.chat.id, "⚠️ Не удалось сохранить изменение.")
            return
        bot.send_message(message.chat.id, f"✅ Счёт обновлён: {score_player}:{score_opponent}.")

    # -------------------- Лог дуэлей: изменение тира до/после --------------------

    @_cbh(lambda c: (c.data or '').startswith('admin:dueledittier:'))
    def handle_duel_edit_tier_request(call):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "⛔ Нет доступа", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        _, _, player_name, kit, date_str, idx_str = _split(call.data, 5)
        msg = bot.edit_message_text(
            f"Игрок: <b>{_esc(player_name)}</b>\nОтправьте новые тиры в формате <code>LT2 HT3</code> "
            f"(сначала «предыдущий», потом «полученный», через пробел; Unranked допустим):",
            call.message.chat.id, call.message.message_id, parse_mode='HTML',
        )
        bot.register_next_step_handler(msg, _handle_duel_tier_input, gh_repo, gh_token, player_name, kit, date_str, int(idx_str))

    def _handle_duel_tier_input(message, gh_repo, gh_token, player_name, kit, date_str, idx):
        if not is_admin(message.from_user.id):
            return
        raw = _input_text(bot, message)
        if raw is None:
            return
        parts_text = raw.split()
        if len(parts_text) != 2:
            bot.send_message(message.chat.id, "⚠️ Нужно ровно два значения через пробел, например «LT2 HT3». Повторите /admin.")
            return
        tier_before, tier_after = parts_text[0], parts_text[1]
        valid_values = set(ALL_TIERS) | {"Unranked"}
        if tier_before not in valid_values or tier_after not in valid_values:
            bot.send_message(
                message.chat.id,
                f"⚠️ Неизвестный тир. Допустимые значения: {', '.join(ALL_TIERS)}, Unranked. Повторите /admin.",
            )
            return

        ok = _apply_mutation(
            gh_repo, gh_token,
            lambda players_list, pn=player_name, i=idx, tb=tier_before, ta=tier_after: _mutate_edit_duel_tiers(players_list, pn, i, tb, ta),
            f"Админ-панель: изменены тиры в записи лога дуэлей {player_name} ({kit}, {date_str})",
            bot=bot, chat_id=message.chat.id, message_id=None,
        )
        if not ok:
            bot.send_message(message.chat.id, "⚠️ Не удалось сохранить изменение.")
            return
        bot.send_message(message.chat.id, f"✅ Тиры обновлены: {tier_before} → {tier_after}.")


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


def _mutate_freeze_all(players_list, player_name, retired_value: bool):
    """
    Массово ставит/снимает retired на ВСЕХ китах игрока, чей тир входит в
    RETIRED_ELIGIBLE_TIERS (HT1-HT3). Киты ниже HT3 не трогает - сайт не
    поддерживает для них статус Retired (см. parseTierInfo во фронтенде).
    """
    player = _find_player(players_list, player_name)
    if not player:
        raise RuntimeError(f"Игрок {player_name} не найден")
    changed_any = False
    for kit, data in player.get('tiers', {}).items():
        if data.get('tier') in RETIRED_ELIGIBLE_TIERS:
            data['retired'] = retired_value
            changed_any = True
    if not changed_any:
        raise RuntimeError(f"У {player_name} нет китов в диапазоне {', '.join(RETIRED_ELIGIBLE_TIERS)}")
    return players_list


def _mutate_delete_duel_entry(players_list, player_name, idx):
    player = _find_player(players_list, player_name)
    if not player:
        raise RuntimeError(f"Игрок {player_name} не найден")
    history = player.get('matchHistory', [])
    if idx < 0 or idx >= len(history):
        raise RuntimeError("Запись не найдена (индекс вне диапазона - возможно, база изменилась)")
    history.pop(idx)
    return players_list


def _mutate_edit_duel_score(players_list, player_name, idx, score_player, score_opponent):
    player = _find_player(players_list, player_name)
    if not player:
        raise RuntimeError(f"Игрок {player_name} не найден")
    history = player.get('matchHistory', [])
    if idx < 0 or idx >= len(history):
        raise RuntimeError("Запись не найдена (индекс вне диапазона - возможно, база изменилась)")
    entry = history[idx]
    entry['scorePlayer'] = score_player
    # Пишем в оба возможных поля - новое (scoreOpponent) и старое
    # (scoreTester), в зависимости от того, какое уже использовалось в
    # этой записи, чтобы не создавать дублирующее поле вперемешку со старым.
    if 'scoreTester' in entry and 'scoreOpponent' not in entry:
        entry['scoreTester'] = score_opponent
    else:
        entry['scoreOpponent'] = score_opponent
    # Пересчитываем победителя по новому счёту, раз счёт меняется вручную -
    # иначе останется рассинхрон между winner и реальными цифрами.
    entry['winner'] = 'player' if score_player > score_opponent else 'opponent'
    return players_list


def _mutate_edit_duel_tiers(players_list, player_name, idx, tier_before, tier_after):
    player = _find_player(players_list, player_name)
    if not player:
        raise RuntimeError(f"Игрок {player_name} не найден")
    history = player.get('matchHistory', [])
    if idx < 0 or idx >= len(history):
        raise RuntimeError("Запись не найдена (индекс вне диапазона - возможно, база изменилась)")
    entry = history[idx]
    entry['tierBefore'] = None if tier_before == "Unranked" else tier_before
    entry['tierAfter'] = None if tier_after == "Unranked" else tier_after
    return players_list


def _mutate_apply_penalty_with_demotion(players_list, player_name, kit, new_points, first_penalty_date, demote: bool):
    """
    То же самое, что _mutate_apply_penalty, но если demote=True - также
    понижает тир на кит на одну ступень (next_tier_down) и обнуляет
    штрафные очки, ТОЧНО повторяя поведение обычного авто-понижения при
    штрафе за тест (см. main.py apply_penalty_and_check_demotion).
    """
    player = _find_player(players_list, player_name)
    if not player:
        raise RuntimeError(f"Игрок {player_name} не найден")

    if not demote:
        player.setdefault('penaltyByKit', {})[kit] = {
            "points": new_points,
            "firstPenaltyDate": first_penalty_date,
        }
        return players_list

    current_tier = player.get('tiers', {}).get(kit, {}).get('tier')
    lower_tier = next_tier_down(current_tier) if current_tier else None

    if lower_tier:
        player.setdefault('tiers', {})[kit] = {
            "tier": lower_tier,
            "date": today_str(),
            "retired": False,
        }
        player.setdefault('matchHistory', []).append({
            "date": today_str(),
            "kit": kit,
            "opponent": "система",
            "tierBefore": current_tier,
            "tierAfter": lower_tier,
            "scorePlayer": None,
            "scoreOpponent": None,
            "winner": None,
            "comment": "Автопонижение за штрафные очки (админ-панель)",
        })

    # Очки штрафа обнуляются независимо от того, было ли фактическое
    # понижение (например tier уже LT5, понижать некуда) - таково же
    # поведение обычного авто-понижения в penalty_logic/main.py.
    player.setdefault('penaltyByKit', {})[kit] = {"points": 0.0, "firstPenaltyDate": today_str()}
    return players_list


def _format_duel_entry(player_name, kit, date_str, entry):
    opponent = entry.get('opponent') or entry.get('tester') or '?'
    score_player = entry.get('scorePlayer', '?')
    score_opponent = entry.get('scoreOpponent', entry.get('scoreTester', '?'))
    tier_before = entry.get('tierBefore') or 'Unranked'
    tier_after = entry.get('tierAfter') or 'Unranked'
    comment = entry.get('comment')
    lines = [
        f"Игрок: <b>{_esc(player_name)}</b>",
        f"Кит: <b>{_esc(kit)}</b>",
        f"Дата: {date_str}",
        f"Оппонент: {_esc(opponent)}",
        f"Счёт: {score_player}:{score_opponent}",
        f"Тир: {tier_before} → {tier_after}",
    ]
    if comment:
        lines.append(f"Комментарий: <i>{_esc(comment)}</i>")
    lines.append("\nВыберите действие:")
    return "\n".join(lines)


def _apply_penalty_change(bot, gh_repo, gh_token, chat_id, message_id, player_name, kit, delta):
    """Применяет +delta к текущим штрафным очкам (используется кнопками +0.5/-0.5)."""
    players_list = _fetch_players(gh_repo, gh_token)
    player = _find_player(players_list, player_name)
    if not player:
        bot.edit_message_text(f"⚠️ Игрок {player_name} не найден.", chat_id, message_id, reply_markup=_main_menu_keyboard())
        return

    current_entry = player.get('penaltyByKit', {}).get(kit)
    current_points = current_entry.get('points', 0.0) if current_entry else 0.0
    new_points = max(0.0, current_points + delta)  # штраф не уходит в минус
    first_date = current_entry.get('firstPenaltyDate') if current_entry else today_str()

    _finalize_penalty_change(bot, gh_repo, gh_token, chat_id, message_id, player_name, kit, new_points, first_date)


def _apply_penalty_set(bot, gh_repo, gh_token, chat_id, message_id, player_name, kit, new_points):
    """Устанавливает точное значение штрафных очков (используется вводом текста)."""
    if new_points < 0:
        bot.send_message(chat_id, "⚠️ Штрафные очки не могут быть отрицательными.")
        return

    players_list = _fetch_players(gh_repo, gh_token)
    player = _find_player(players_list, player_name)
    if not player:
        bot.send_message(chat_id, f"⚠️ Игрок {player_name} не найден.")
        return

    current_entry = player.get('penaltyByKit', {}).get(kit)
    first_date = current_entry.get('firstPenaltyDate') if current_entry else today_str()

    _finalize_penalty_change(bot, gh_repo, gh_token, chat_id, message_id, player_name, kit, new_points, first_date)


def _finalize_penalty_change(bot, gh_repo, gh_token, chat_id, message_id, player_name, kit, new_points, first_date):
    """
    Общий финальный шаг для +0.5/-0.5 и "точное число": решает, нужно ли
    авто-понижение (new_points >= PENALTY_DEMOTION_THRESHOLD), и
    применяет изменение через update_players_file. Если message_id
    отсутствует (значит, вызов пришёл из текстового ввода, а не из
    callback), результат отправляется новым сообщением.
    """
    demote = new_points >= PENALTY_DEMOTION_THRESHOLD

    ok = _apply_mutation(
        gh_repo, gh_token,
        lambda players_list, pn=player_name, k=kit, np=new_points, fd=first_date, d=demote:
            _mutate_apply_penalty_with_demotion(players_list, pn, k, np, fd, d),
        f"Админ-панель: штрафные очки {player_name} / {kit} -> {new_points}"
        + (" (авто-понижение)" if demote else ""),
        bot=(bot if message_id is not None else None),
        chat_id=chat_id, message_id=message_id,
    )

    if not ok:
        if message_id is None:
            bot.send_message(chat_id, "⚠️ Не удалось сохранить изменение штрафных очков.")
        return

    if demote:
        text = (
            f"⚠️ Штрафные очки {player_name} / {kit} достигли {new_points} (порог {PENALTY_DEMOTION_THRESHOLD}) - "
            f"тир автоматически понижен, штраф обнулён."
        )
    else:
        text = f"✅ Готово. Штрафные очки {player_name} / {kit}: {new_points}."

    if message_id is not None:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=_main_menu_keyboard())
    else:
        bot.send_message(chat_id, text)
