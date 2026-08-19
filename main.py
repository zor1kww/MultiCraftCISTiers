# -*- coding: utf-8 -*-
"""
Telegram-бот тир-тестера MultiCraftCISTiers.

Архитектура: вся бизнес-логика уже написана и протестирована отдельно
(без сети/telebot) в модулях:
  - bot_config.py     - справочники (тестеры, киты, регионы, тиры)
  - tier_logic.py      - математика тиров, Retired-правило, тексты карточек
  - fsm.py              - машина состояний диалога
  - github_storage.py  - чтение/запись players.js на GitHub

Этот файл - только обвязка telebot: клавиатуры, обработчики сообщений/
кнопок, отправка карточек в нужный топик. ВАЖНО: этот файл писался и
проверялся синтаксически, но БЕЗ доступа к реальному Telegram API и без
установленного pyTelegramBotAPI (нет сети в среде разработки) - перед
тем как давать доступ остальным тестерам, обязательно прогони полный
диалог сам и проверь каждую ветку.
"""

import os
import traceback
from threading import Thread

import telebot
from telebot import types
from flask import Flask

from bot_config import (
    TESTERS, is_authorized_tester, VALID_KITS, MAIN_KITS, SUB_KITS,
    REGIONS, TIER_ORDER, RETIRED_ELIGIBLE_TIERS, RESULTS_CHAT_ID,
    RESULTS_THREAD_ID, HIGH_RESULTS_THREAD_ID,
)
from tier_logic import (
    calculate_overall_tier, determine_topic, tester_mention,
    build_high_test_card, build_normal_result_card, build_tier_object,
    today_str,
)
from fsm import (
    DialogState, start_dialog, get_dialog, end_dialog,
    STEP_TEST_OR_ADMIN, STEP_PLAYER_NAME, STEP_KIT, STEP_REGION,
    STEP_TIER_BEFORE, STEP_TIER_TESTED, STEP_PASSED, STEP_TIER_AFTER,
    STEP_NO_TEST_REASON, STEP_RETIRED_CHOICE, STEP_DUELS_COUNT,
    STEP_DUEL_OPPONENT, STEP_DUEL_SCORE, STEP_TESTER_SELECT,
    STEP_COMMENT, STEP_PREVIEW, STEP_DONE,
    advance_after_test_or_admin, advance_after_player_name, advance_after_kit,
    advance_after_region, advance_after_tier_before, advance_after_tier_tested,
    advance_after_passed, advance_after_tier_after, advance_after_no_test_reason,
    advance_after_retired_choice, advance_after_duels_count,
    advance_after_duel_opponent, advance_after_duel_score,
    advance_after_tester_select, advance_after_comment, confirm_preview,
    validate_player_name, validate_score, validate_comment, validate_duels_count,
)
import github_storage


# ==========================================
# НАСТРОЙКА
# ==========================================

app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)


TG_TOKEN = os.environ.get('TG_TOKEN')
GH_TOKEN = os.environ.get('GH_TOKEN')
GH_REPO = os.environ.get('GH_REPO')

bot = telebot.TeleBot(TG_TOKEN)


# ==========================================
# КНОПКИ (inline-клавиатуры для каждого шага)
# ==========================================

def kb_test_or_admin():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🥊 Прошёл тир-тест", callback_data="ta:test"))
    kb.add(types.InlineKeyboardButton("⚙️ Изменение без теста", callback_data="ta:admin"))
    return kb


def kb_kits():
    kb = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(k, callback_data=f"kit:{k}") for k in VALID_KITS]
    kb.add(*buttons)
    return kb


def kb_regions():
    kb = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(r, callback_data=f"region:{r}") for r in REGIONS]
    kb.add(*buttons)
    return kb


def kb_tiers(callback_prefix: str, include_unranked: bool = True):
    kb = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(t, callback_data=f"{callback_prefix}:{t}") for t in TIER_ORDER]
    kb.add(*buttons)
    if include_unranked:
        kb.add(types.InlineKeyboardButton("Unranked", callback_data=f"{callback_prefix}:Unranked"))
    return kb


def kb_yes_no(prefix: str, yes_label="✅ Да", no_label="❌ Нет"):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(yes_label, callback_data=f"{prefix}:yes"),
        types.InlineKeyboardButton(no_label, callback_data=f"{prefix}:no"),
    )
    return kb


def kb_retired_choice():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("💤 Отправить в Retired", callback_data="retired:yes"))
    kb.add(types.InlineKeyboardButton("▶️ Оставить активным", callback_data="retired:no"))
    return kb


def kb_testers(exclude_self_id: int = None):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for tid, tname in TESTERS.items():
        label = f"{tname}" + (" (я)" if tid == exclude_self_id else "")
        kb.add(types.InlineKeyboardButton(label, callback_data=f"tester:{tid}"))
    return kb


def kb_comment_skip():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Пропустить", callback_data="comment:skip"))
    return kb


def kb_preview():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ Отправить", callback_data="preview:send"))
    kb.add(types.InlineKeyboardButton("❌ Отменить", callback_data="preview:cancel"))
    return kb


def kb_after_send():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("➕ Внести ещё один результат", callback_data="restart:new"))
    return kb


# ==========================================
# ТЕКСТЫ ПРОМЕЖУТОЧНЫХ ШАГОВ
# ==========================================

STEP_PROMPTS = {
    STEP_PLAYER_NAME: "Введите ник игрока:",
    STEP_KIT: "Выберите кит:",
    STEP_REGION: "Выберите регион:",
    STEP_TIER_BEFORE: "Какой ранг был у игрока до этого события?\n(если игрок новый - выберите Unranked)",
    STEP_TIER_TESTED: "На какой ранг тестировался игрок?",
    STEP_PASSED: "Игрок сдал тест?",
    STEP_TIER_AFTER: "Какой ранг присваивается игроку?",
    STEP_NO_TEST_REASON: "Укажите причину изменения ранга:",
    STEP_RETIRED_CHOICE: "Этот ранг (HT3 и выше) может получить статус Retired.\nОтправить игрока в Retired по этому киту?",
    STEP_DUELS_COUNT: "Сколько было поединков? (1-6)",
    STEP_TESTER_SELECT: "Кто был тир-тестером?",
    STEP_COMMENT: "Комментарий (необязательно) - напишите текстом или нажмите «Пропустить»:",
}


def send_step_prompt(chat_id, state: DialogState, message_id=None):
    """Отправляет (или редактирует) сообщение с промптом текущего шага и нужной клавиатурой."""
    step = state.step
    text = STEP_PROMPTS.get(step, "...")

    keyboard = None
    if step == STEP_TEST_OR_ADMIN:
        text = "Что произошло с игроком?"
        keyboard = kb_test_or_admin()
    elif step == STEP_KIT:
        keyboard = kb_kits()
    elif step == STEP_REGION:
        keyboard = kb_regions()
    elif step == STEP_TIER_BEFORE:
        keyboard = kb_tiers("tb")
    elif step == STEP_TIER_TESTED:
        # Тестировать можно только на HT3 и выше (высокие тесты) -
        # если понадобится тестировать на LT3 и ниже, это квалификационный
        # тест, но по договорённости он попадает в топик "Результаты"
        # так же через ветку is_test=True с любым тиром, поэтому здесь
        # даём полный список тиров, не только HT3+.
        keyboard = kb_tiers("tt")
    elif step == STEP_PASSED:
        keyboard = kb_yes_no("passed", "✅ Сдал", "❌ Не сдал")
    elif step == STEP_TIER_AFTER:
        keyboard = kb_tiers("ta_tier")
    elif step == STEP_RETIRED_CHOICE:
        keyboard = kb_retired_choice()
    elif step == STEP_TESTER_SELECT:
        keyboard = kb_testers(exclude_self_id=state.tester_id)
    elif step == STEP_COMMENT:
        keyboard = kb_comment_skip()
    elif step == STEP_DUEL_OPPONENT:
        idx = len(state.duels) + 1
        text = f"Поединок {idx}/{state.duels_expected}. Ник соперника:"
    elif step == STEP_DUEL_SCORE:
        text = f"Счёт (например 10-6):"
    elif step == STEP_PREVIEW:
        text = build_preview_text(state)
        keyboard = kb_preview()

    if message_id:
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
            return
        except Exception:
            pass  # если нечего редактировать (например текст не менялся) - просто отправим новое

    bot.send_message(chat_id, text, reply_markup=keyboard)


# ==========================================
# СБОРКА ПРЕВЬЮ И ФИНАЛЬНОЙ КАРТОЧКИ
# ==========================================

def resolve_tester_mention_for_state(state: DialogState) -> str:
    """Кто фигурирует как тир-тестер в карточке - сам отправитель или другой,
    если он выбрал другого тестера на шаге tester_select."""
    tester_id = state.other_tester_id or state.tester_id
    username = state.tester_username if tester_id == state.tester_id else None
    return tester_mention(tester_id, username)


def build_preview_text(state: DialogState) -> str:
    header = "Проверьте данные перед отправкой:\n\n"
    body = render_card_text(state, for_preview=True)
    footer = f"\n\nТопик: {'Высокие результаты' if determine_topic(state.tier_after) == 'high' else 'Результаты'}"
    return header + body + footer


def render_card_text(state: DialogState, for_preview: bool = False) -> str:
    """
    Строит финальный текст карточки. Для превью overall_tier/tests_count
    считаются по ТЕКУЩИМ данным игрока (без применения ещё не сохранённого
    изменения) - небольшая неточность в превью (средний ранг ещё не
    учитывает вносимый результат), но она не критична: превью нужно для
    проверки введённых данных, а финальное сообщение после реальной записи
    в GitHub уже покажет точный пересчитанный средний ранг.
    """
    tester_str = resolve_tester_mention_for_state(state)

    # overall_tier/tests_count будут пересчитаны точно в момент реальной записи
    # (после mutate_fn в github_storage) - для превью используем заглушку 0/Unranked,
    # реальные значения подставляются в send_final_card() после записи в БД.
    overall_tier = getattr(state, '_preview_overall_tier', 'Unranked')
    tests_count = getattr(state, '_preview_tests_count', 0)

    if state.is_test:
        return build_high_test_card(
            player_name=state.player_name,
            region=state.region,
            kit=state.kit,
            tier_before=state.tier_before,
            tier_after=state.tier_after,
            tier_tested=state.tier_tested,
            passed=state.passed,
            duels=state.duels,
            tester_mention_str=tester_str,
            comment=state.comment,
            overall_tier=overall_tier,
            tests_count=tests_count,
        )
    else:
        is_new = state.tier_before == "Unranked"
        return build_normal_result_card(
            player_name=state.player_name,
            region=state.region,
            kit=state.kit,
            tier_before=state.tier_before,
            tier_after=state.tier_after,
            is_new_player_kit=is_new,
            tester_mention_str=tester_str,
            comment=None,
            overall_tier=overall_tier,
            tests_count=tests_count,
            no_test_reason=state.no_test_reason,
        )


def find_player(players_list, name: str):
    name_lower = name.lower()
    for p in players_list:
        if p.get('name', '').lower() == name_lower:
            return p
    return None


def apply_result_to_players_list(players_list, state: DialogState):
    """
    Мутирует players_list, применяя результат из state. Возвращает
    (players_list, overall_tier, tests_count) - последние два нужны
    для текста финальной карточки.
    """
    player = find_player(players_list, state.player_name)

    tier_obj = build_tier_object(state.tier_after, retired=state.retired, test_date=today_str())

    if player is None:
        player = {
            "name": state.player_name,
            "region": state.region,
            "tiers": {state.kit: tier_obj},
        }
        players_list.append(player)
    else:
        player['region'] = state.region
        if 'tiers' not in player:
            player['tiers'] = {}
        player['tiers'][state.kit] = tier_obj

    overall_tier, tests_count = calculate_overall_tier(player['tiers'])
    return players_list, overall_tier, tests_count


def send_final_card(state: DialogState):
    """Записывает результат в GitHub и постит карточку в нужный топик."""
    result_holder = {}

    def mutate(players_list):
        updated_list, overall_tier, tests_count = apply_result_to_players_list(players_list, state)
        result_holder['overall_tier'] = overall_tier
        result_holder['tests_count'] = tests_count
        return updated_list

    commit_message = f"result: {state.player_name} -> {state.kit} ({state.tier_after})"
    github_storage.update_players_file(GH_REPO, GH_TOKEN, mutate, commit_message)

    state._preview_overall_tier = result_holder['overall_tier']
    state._preview_tests_count = result_holder['tests_count']

    card_text = render_card_text(state)
    topic = determine_topic(state.tier_after)
    thread_id = HIGH_RESULTS_THREAD_ID if topic == 'high' else RESULTS_THREAD_ID

    send_kwargs = {"chat_id": RESULTS_CHAT_ID, "text": card_text}
    if thread_id is not None:
        send_kwargs["message_thread_id"] = thread_id

    bot.send_message(**send_kwargs)


# ==========================================
# ОБРАБОТЧИКИ TELEGRAM
# ==========================================

@bot.message_handler(commands=['start', 'newresult'])
def handle_start(message):
    user_id = message.from_user.id
    if not is_authorized_tester(user_id):
        bot.reply_to(message, "У вас нет доступа к этому боту.")
        return

    state = start_dialog(user_id, message.from_user.username)
    send_step_prompt(message.chat.id, state)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    if not is_authorized_tester(user_id):
        bot.answer_callback_query(call.id, "Нет доступа.")
        return

    state = get_dialog(user_id)
    if state is None:
        bot.answer_callback_query(call.id, "Диалог не найден, начните заново: /start")
        return

    bot.answer_callback_query(call.id)
    data = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    try:
        prefix, _, value = data.partition(':')

        if prefix == "ta" and state.step == STEP_TEST_OR_ADMIN:
            advance_after_test_or_admin(state, value == "test")

        elif prefix == "kit" and state.step == STEP_KIT:
            advance_after_kit(state, value)

        elif prefix == "region" and state.step == STEP_REGION:
            advance_after_region(state, value)

        elif prefix == "tb" and state.step == STEP_TIER_BEFORE:
            advance_after_tier_before(state, value)

        elif prefix == "tt" and state.step == STEP_TIER_TESTED:
            advance_after_tier_tested(state, value)

        elif prefix == "passed" and state.step == STEP_PASSED:
            advance_after_passed(state, value == "yes")

        elif prefix == "ta_tier" and state.step == STEP_TIER_AFTER:
            advance_after_tier_after(state, value)

        elif prefix == "retired" and state.step == STEP_RETIRED_CHOICE:
            advance_after_retired_choice(state, value == "yes")

        elif prefix == "tester" and state.step == STEP_TESTER_SELECT:
            advance_after_tester_select(state, int(value))

        elif prefix == "comment" and state.step == STEP_COMMENT and value == "skip":
            advance_after_comment(state, None)

        elif prefix == "preview" and state.step == STEP_PREVIEW:
            if value == "send":
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="⏳ Записываю результат...")
                send_final_card(state)
                bot.send_message(chat_id, "✅ Результат отправлен и записан в базу.", reply_markup=kb_after_send())
                end_dialog(user_id)
                return
            else:
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="❌ Отменено.")
                end_dialog(user_id)
                return

        elif prefix == "restart" and value == "new":
            new_state = start_dialog(user_id, call.from_user.username)
            send_step_prompt(chat_id, new_state)
            return

        else:
            # Кнопка не соответствует текущему шагу (например, повторный тап
            # на устаревшей клавиатуре) - игнорируем молча
            return

        send_step_prompt(chat_id, state, message_id=message_id)

    except Exception as e:
        traceback.print_exc()
        bot.send_message(chat_id, f"⚠️ Произошла ошибка: {e}\nНачните заново: /start")
        end_dialog(user_id)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    if not is_authorized_tester(user_id):
        return  # молчим на сообщения от посторонних, чтобы не шуметь в личке

    state = get_dialog(user_id)
    if state is None:
        bot.reply_to(message, "Чтобы начать вносить результат, отправьте /start")
        return

    text = message.text.strip()

    try:
        if state.step == STEP_PLAYER_NAME:
            ok, result = validate_player_name(text)
            if not ok:
                bot.reply_to(message, f"⚠️ {result}")
                return
            advance_after_player_name(state, result)

        elif state.step == STEP_NO_TEST_REASON:
            ok, result = validate_comment(text)  # тот же лимит длины уместен и тут
            if not ok:
                bot.reply_to(message, f"⚠️ {result}")
                return
            advance_after_no_test_reason(state, result)

        elif state.step == STEP_DUELS_COUNT:
            ok, result = validate_duels_count(text)
            if not ok:
                bot.reply_to(message, f"⚠️ {result}")
                return
            advance_after_duels_count(state, result)

        elif state.step == STEP_DUEL_OPPONENT:
            ok, result = validate_player_name(text)  # те же ограничения на ник
            if not ok:
                bot.reply_to(message, f"⚠️ {result}")
                return
            advance_after_duel_opponent(state, result)

        elif state.step == STEP_DUEL_SCORE:
            ok, result = validate_score(text)
            if not ok:
                bot.reply_to(message, f"⚠️ {result}")
                return
            advance_after_duel_score(state, result)

        elif state.step == STEP_COMMENT:
            ok, result = validate_comment(text)
            if not ok:
                bot.reply_to(message, f"⚠️ {result}")
                return
            advance_after_comment(state, result)

        else:
            # Текст пришёл не на том шаге, где ожидается (сейчас должна быть
            # кнопка) - подсказываем вместо того чтобы молча игнорировать
            bot.reply_to(message, "Пожалуйста, используйте кнопки выше для этого шага.")
            return

        send_step_prompt(message.chat.id, state)

    except Exception as e:
        traceback.print_exc()
        bot.reply_to(message, f"⚠️ Произошла ошибка: {e}\nНачните заново: /start")
        end_dialog(user_id)


# ==========================================
# ЗАПУСК
# ==========================================

if __name__ == '__main__':
    print("Запуск веб-сервера для Render...")
    t = Thread(target=run_web_server)
    t.start()

    print("Бот успешно запущен. Ожидаю тир-тестеров...")
    bot.infinity_polling()
