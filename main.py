# -*- coding: utf-8 -*-
"""
Telegram-бот тир-тестера MultiCraftCISTiers (v3 - текстовый шаблон).

Архитектура:
  - Тестеры пишут результаты текстовым шаблоном в закрытой группе,
    топик "Результаты" (SOURCE_CHAT_ID/SOURCE_THREAD_ID из bot_config.py).
  - Бот - обычный участник-админ этой группы, слушает сообщения через
    polling. Так как бот добавлен АДМИНОМ, privacy mode Telegram не
    ограничивает видимость сообщений - бот видит все сообщения в группе.
  - Каждое сообщение в целевом топике пропускается через text_parser:
      * не похоже на результат (нет меток полей) -> молча игнорируется
      * похоже, но с ошибкой (не хватает полей/неверные значения) ->
        бот отвечает в тот же топик с описанием ошибки
      * распознано полностью -> ставится в очередь (result_queue.py)
  - Очередь обрабатывает результаты СТРОГО последовательно с паузой
    5-10 секунд между записями в GitHub - защита от пачек сообщений,
    накопившихся, пока бот был выключен/спал.
  - Каждый результат: запись в players.js (тир + matchHistory),
    публикация карточки в один из двух ПУБЛИЧНЫХ топиков
    (RESULTS_THREAD_ID / HIGH_RESULTS_THREAD_ID) по правилу:
    tier_after в {LT5,LT4,HT5,LT3} -> "Результаты",
    tier_after в {HT3,LT2,HT2,LT1,HT1} -> "Высокие результаты".

Модули с бизнес-логикой (протестированы отдельно от Telegram):
  - text_parser.py    - разбор шаблонного сообщения
  - tier_logic.py      - математика тиров, тексты карточек, matchHistory
  - github_storage.py  - чтение/запись players.js с retry на sha-конфликт
  - result_queue.py    - последовательная очередь с задержкой
  - bot_config.py      - справочники и ID чатов/топиков

ВАЖНО: этот файл писался БЕЗ доступа к реальному Telegram API и без
установленного pyTelegramBotAPI (нет сети в среде разработки) - перед
боевым использованием стоит понаблюдать за первыми результатами
в логах Render и в самих топиках.
"""

import os
import traceback
from threading import Thread

import telebot
from flask import Flask

from bot_config import (
    SOURCE_CHAT_ID, SOURCE_THREAD_ID,
    RESULTS_CHAT_ID, RESULTS_THREAD_ID, HIGH_RESULTS_THREAD_ID,
)
from text_parser import parse_result_message, ParseError
from tier_logic import (
    calculate_overall_tier, determine_topic, tester_display_name,
    build_high_test_card, build_normal_result_card, build_match_history_entry,
    build_tier_object, today_str,
)
from result_queue import ResultQueue
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

result_queue = ResultQueue()


# ==========================================
# ПРИМЕНЕНИЕ РЕЗУЛЬТАТА К БАЗЕ ИГРОКОВ
# ==========================================

def find_player(players_list, name: str):
    name_lower = name.lower()
    for p in players_list:
        if p.get('name', '').lower() == name_lower:
            return p
    return None


def apply_result_to_players_list(players_list, parsed):
    """
    Мутирует players_list: обновляет тир игрока (или создаёт нового
    игрока, если его ещё нет в базе) и добавляет запись в matchHistory.
    Возвращает (players_list, overall_tier, tests_count, is_new_player).
    """
    player = find_player(players_list, parsed.player_name)

    tier_obj = build_tier_object(parsed.tier_after, retired=False, test_date=today_str())
    history_entry = build_match_history_entry(
        kit=parsed.kit,
        tester_name=parsed.tester_name,
        player_name=parsed.player_name,
        tier_before=parsed.tier_before,
        tier_after=parsed.tier_after,
        score_tester=parsed.score_tester,
        score_player=parsed.score_player,
        winner=parsed.winner,
        comment=parsed.comment,
    )

    is_new_player = player is None

    if is_new_player:
        player = {
            "name": parsed.player_name,
            "region": parsed.region,
            "tiers": {parsed.kit: tier_obj},
            "matchHistory": [history_entry],
        }
        players_list.append(player)
    else:
        player['region'] = parsed.region
        if 'tiers' not in player:
            player['tiers'] = {}
        player['tiers'][parsed.kit] = tier_obj
        if 'matchHistory' not in player:
            player['matchHistory'] = []
        player['matchHistory'].append(history_entry)

    overall_tier, tests_count = calculate_overall_tier(player['tiers'])
    return players_list, overall_tier, tests_count, is_new_player


# ==========================================
# ОБРАБОТКА ОДНОГО РЕЗУЛЬТАТА (задача очереди)
# ==========================================

def process_result(parsed, source_message_id):
    """
    Выполняется в очереди (result_queue), последовательно, с паузой
    перед каждым вызовом (кроме первого). Делает запись в GitHub и
    публикует карточку в нужный публичный топик.
    """
    result_holder = {}

    def mutate(players_list):
        updated_list, overall_tier, tests_count, is_new_player = apply_result_to_players_list(players_list, parsed)
        result_holder['overall_tier'] = overall_tier
        result_holder['tests_count'] = tests_count
        result_holder['is_new_player'] = is_new_player
        return updated_list

    commit_message = f"result: {parsed.player_name} -> {parsed.kit} ({parsed.tier_after})"
    github_storage.update_players_file(GH_REPO, GH_TOKEN, mutate, commit_message)

    overall_tier = result_holder['overall_tier']
    tests_count = result_holder['tests_count']
    is_new_player = result_holder['is_new_player']
    tester_display = tester_display_name(parsed.tester_name)

    topic = determine_topic(parsed.tier_after)

    if topic == 'high':
        card_text = build_high_test_card(
            player_name=parsed.player_name,
            region=parsed.region,
            kit=parsed.kit,
            tier_before=parsed.tier_before,
            tier_after=parsed.tier_after,
            score_tester=parsed.score_tester,
            score_player=parsed.score_player,
            winner=parsed.winner,
            tester_display=tester_display,
            comment=parsed.comment,
            overall_tier=overall_tier,
            tests_count=tests_count,
        )
        thread_id = HIGH_RESULTS_THREAD_ID
    else:
        card_text = build_normal_result_card(
            player_name=parsed.player_name,
            region=parsed.region,
            kit=parsed.kit,
            tier_before=parsed.tier_before,
            tier_after=parsed.tier_after,
            is_new_player_kit=is_new_player or parsed.tier_before == "Unranked",
            tester_display=tester_display,
            comment=parsed.comment,
            overall_tier=overall_tier,
            tests_count=tests_count,
        )
        thread_id = RESULTS_THREAD_ID

    send_kwargs = {"chat_id": RESULTS_CHAT_ID, "text": card_text}
    if thread_id is not None:
        send_kwargs["message_thread_id"] = thread_id

    bot.send_message(**send_kwargs)


def handle_processing_error(exc):
    """Вызывается очередью, если process_result упал с исключением.
    Не можем надёжно сослаться на исходное сообщение отсюда (очередь
    уже оторвана от контекста конкретного апдейта) - просто логируем,
    ошибка уже напечатана в traceback самой очередью."""
    print(f"[result_queue] Ошибка обработки результата: {exc}")


# ==========================================
# TELEGRAM: приём сообщений из группы тестеров
# ==========================================

def is_in_source_topic(message) -> bool:
    if message.chat.id != SOURCE_CHAT_ID:
        return False
    # message_thread_id отсутствует у сообщений вне топиков (в основном чате
    # форума) - если SOURCE_THREAD_ID задан, требуем точного совпадения
    return getattr(message, 'message_thread_id', None) == SOURCE_THREAD_ID


@bot.message_handler(func=is_in_source_topic, content_types=['text'])
def handle_source_message(message):
    text = message.text

    try:
        parsed = parse_result_message(text)
    except ParseError as e:
        bot.reply_to(message, f"⚠️ Не удалось разобрать результат: {e}")
        return

    if parsed is None:
        return  # обычное обсуждение в топике, молча игнорируем

    # Ставим в очередь - фактическая запись в GitHub и отправка карточки
    # произойдёт последовательно, с паузой относительно других задач в очереди
    result_queue.submit(lambda: process_result(parsed, message.message_id))


# ==========================================
# ЗАПУСК
# ==========================================

if __name__ == '__main__':
    print("Запуск веб-сервера для Render...")
    t = Thread(target=run_web_server)
    t.start()

    print("Запуск очереди обработки результатов...")
    result_queue._on_task_error = handle_processing_error
    result_queue.start()

    print("Бот успешно запущен. Слушаю группу тестеров...")
    bot.infinity_polling()
