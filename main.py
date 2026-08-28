# -*- coding: utf-8 -*-
"""
Telegram-бот тир-тестера MultiCraftCISTiers (v4 - Оппонент/Игрок, симметричные штрафы).

Архитектура:
  - Тестеры пишут результаты текстовым шаблоном в закрытой группе,
    топик "Результаты" (SOURCE_CHAT_ID/SOURCE_THREAD_ID из bot_config.py).
  - Бот - обычный участник-админ этой группы, слушает сообщения через
    polling. Так как бот добавлен АДМИНОМ, privacy mode Telegram не
    ограничивает видимость сообщений.
  - Шаблон теперь без роли "Тестер" - только "Оппонент:" (один или
    несколько через запятую) и "Игрок:" (тот, кто тестируется на новый
    ранг - может быть как раньше "тестируемым", так и выигравшим
    оппонентом, тестеры сами решают, кого писать в это поле).
  - Каждое сообщение в целевом топике пропускается через text_parser:
      * не похоже на результат (нет меток полей) -> молча игнорируется
      * похоже, но с ошибкой -> бот отвечает в тот же топик с описанием
      * распознано полностью -> ставится в очередь (result_queue.py)
  - Очередь обрабатывает результаты СТРОГО последовательно с паузой
    5-10 секунд между записями в GitHub.
  - Штрафные очки (только для HT3+ результатов) считаются СИММЕТРИЧНО
    и ПОДУЭЛЬНО: для каждой дуэли отдельно проверяется, кто проиграл и
    был ли он равного/выше ранга - см. penalty_logic.apply_penalty_for_duel.
  - Каждый результат: запись в players.js (тир игрока + matchHistory -
    по одной записи на КАЖДУЮ дуэль), публикация карточки в один из
    двух публичных топиков по правилу determine_topic(tier_after).

Модули с бизнес-логикой (протестированы отдельно от Telegram):
  - text_parser.py    - разбор шаблонного сообщения (Оппонент/Счёт)
  - tier_logic.py      - математика тиров, единая карточка, matchHistory
  - penalty_logic.py   - симметричные штрафы подуэльно, автопонижение
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
    PENALTY_DEMOTION_THRESHOLD,
)
from text_parser import parse_result_message, ParseError
from tier_logic import (
    calculate_overall_tier, determine_topic,
    build_result_card, build_match_history_entry,
    build_tier_object, build_penalty_demotion_card, today_str,
)
from penalty_logic import apply_penalty_for_duel, next_tier_down, add_penalty_to_entry
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


def get_player_tier_on_kit(players_list, player_name: str, kit: str):
    """Возвращает строку тира игрока на данном ките, или None если игрока
    нет в базе или у него нет записи по этому киту."""
    player = find_player(players_list, player_name)
    if player is None:
        return None
    tier_obj = player.get('tiers', {}).get(kit)
    if tier_obj is None:
        return None
    return tier_obj.get('tier') if isinstance(tier_obj, dict) else tier_obj


def ensure_player_exists(players_list, name, region):
    """Возвращает существующего игрока по имени или создаёт нового с
    пустыми tiers/matchHistory/penaltyByKit, добавляя его в players_list."""
    player = find_player(players_list, name)
    if player is None:
        player = {
            "name": name,
            "region": region,
            "tiers": {},
            "matchHistory": [],
            "penaltyByKit": {},
        }
        players_list.append(player)
        return player, True

    if 'tiers' not in player:
        player['tiers'] = {}
    if 'matchHistory' not in player:
        player['matchHistory'] = []
    if 'penaltyByKit' not in player:
        player['penaltyByKit'] = {}
    return player, False


def apply_result_to_players_list(players_list, parsed):
    """
    Мутирует players_list:
      1. Обновляет тир ИГРОКА (parsed.player_name) на parsed.tier_after,
         создаёт его в базе, если ещё нет.
      2. Добавляет в matchHistory игрока ПО ОДНОЙ записи на каждую дуэль
         из parsed.duels (для многодуэльного HT1-теста это несколько
         записей за один результат).
      2b. Симметрично добавляет запись об этой же дуэли и В MATCHHISTORY
          ОППОНЕНТА (duel.opponent), создавая его в базе, если его там ещё
          нет. Со стороны оппонента tierBefore/tierAfter - это ЕГО
          собственный тир на этом ките (matchHistory хранит тир владельца
          записи, а не игрока-инициатора результата) - у оппонента он не
          меняется этим результатом, только в apply_penalty_and_check_demotion
          при штрафном автопонижении. Счёт и сторона победителя зеркально
          инвертированы, чтобы запись читалась корректно "от лица" оппонента.
      3. Если результат относится к HT3+ (determine_topic == 'high') -
         для каждой дуэли отдельно вычисляет и применяет штраф
         (см. penalty_logic.apply_penalty_for_duel), с возможным
         автопонижением как игрока, так и любого из оппонентов.

    Возвращает (players_list, overall_tier, demotions).
    demotions - список dict для карточек автопонижения.
    """
    player, _ = ensure_player_exists(players_list, parsed.player_name, parsed.region)
    player['region'] = parsed.region

    tier_obj = build_tier_object(parsed.tier_after, retired=False, test_date=today_str())
    player['tiers'][parsed.kit] = tier_obj

    for duel in parsed.duels:
        player['matchHistory'].append(build_match_history_entry(
            kit=parsed.kit,
            opponent_name=duel.opponent,
            player_name=parsed.player_name,
            tier_before=parsed.tier_before,
            tier_after=parsed.tier_after,
            score_player=duel.score_player,
            score_opponent=duel.score_opponent,
            winner=duel.winner,
            comment=parsed.comment,
        ))

        # Симметричная запись у оппонента - "" вместо региона: если оппонент
        # заводится в базе впервые, его настоящий регион неизвестен из этого
        # шаблона (в нём указан только регион parsed.player_name); при
        # следующем результате, где уже сам оппонент - player_name, регион
        # проставится корректно через ensure_player_exists/player['region'].
        opponent_player, _ = ensure_player_exists(players_list, duel.opponent, "")
        opponent_tier_now = get_player_tier_on_kit(players_list, duel.opponent, parsed.kit)
        opponent_player['matchHistory'].append(build_match_history_entry(
            kit=parsed.kit,
            opponent_name=parsed.player_name,
            player_name=duel.opponent,
            tier_before=opponent_tier_now,
            tier_after=opponent_tier_now,
            score_player=duel.score_opponent,
            score_opponent=duel.score_player,
            winner=("player" if duel.winner == "opponent" else "opponent"),
            comment=parsed.comment,
        ))

    overall_tier, _ = calculate_overall_tier(player['tiers'])

    demotions = []
    if determine_topic(parsed.tier_after) == 'high':
        for duel in parsed.duels:
            demotions.extend(apply_penalty_and_check_demotion(players_list, parsed, duel))

    return players_list, overall_tier, demotions


def apply_penalty_and_check_demotion(players_list, parsed, duel):
    """
    Вычисляет и применяет штраф ЗА ОДНУ дуэль (симметрично: может
    оштрафовать либо игрока, либо конкретного оппонента этой дуэли), с
    возможным автопонижением, если порог достигнут.

    Возвращает список демоций (0 или 1 элемент), произошедших в
    результате обработки этой конкретной дуэли.
    """
    def get_tier_fn(name, kit):
        return get_player_tier_on_kit(players_list, name, kit)

    penalty_result = apply_penalty_for_duel(
        kit=parsed.kit,
        player_name=parsed.player_name,
        opponent_name=duel.opponent,
        tier_before_player=parsed.tier_before,
        score_player=duel.score_player,
        score_opponent=duel.score_opponent,
        winner=duel.winner,
        get_player_tier_fn=get_tier_fn,
    )

    demotions = []

    for entry in penalty_result.entries:
        target_name = entry["player_name"]
        kit = entry["kit"]
        added = entry["penalty_added"]

        target_player, _ = ensure_player_exists(players_list, target_name, "")

        current_entry = target_player['penaltyByKit'].get(kit)
        new_entry = add_penalty_to_entry(current_entry, added, today_str())
        new_penalty = new_entry["points"]

        if new_penalty >= PENALTY_DEMOTION_THRESHOLD:
            current_tier = get_player_tier_on_kit(players_list, target_name, kit)
            new_tier = next_tier_down(current_tier) if current_tier else None

            if new_tier is not None:
                target_player['tiers'][kit] = build_tier_object(new_tier, retired=False)
                target_player['penaltyByKit'][kit] = {"points": 0.0, "firstPenaltyDate": today_str()}

                target_player['matchHistory'].append(build_match_history_entry(
                    kit=kit, opponent_name="система", player_name=target_name,
                    tier_before=current_tier, tier_after=new_tier,
                    score_player=0, score_opponent=0, winner="opponent",
                    comment=f"Автопонижение: накоплено {PENALTY_DEMOTION_THRESHOLD:g} штрафных очка",
                ))

                overall_tier, _ = calculate_overall_tier(target_player['tiers'])

                demotions.append({
                    "player_name": target_name,
                    "kit": kit,
                    "old_tier": current_tier,
                    "new_tier": new_tier,
                    "overall_tier": overall_tier,
                })
            else:
                target_player['penaltyByKit'][kit] = new_entry
        else:
            target_player['penaltyByKit'][kit] = new_entry

    return demotions


# ==========================================
# ОБРАБОТКА ОДНОГО РЕЗУЛЬТАТА (задача очереди)
# ==========================================

def process_result(parsed, source_message_id):
    """
    Выполняется в очереди (result_queue), последовательно, с паузой
    перед каждым вызовом (кроме первого). Делает запись в GitHub и
    публикует карточку в нужный публичный топик. Если результат вызвал
    штрафное автопонижение - публикует также отдельную карточку
    понижения для каждого затронутого игрока/оппонента.
    """
    result_holder = {}

    def mutate(players_list):
        updated_list, overall_tier, demotions = apply_result_to_players_list(players_list, parsed)
        result_holder['overall_tier'] = overall_tier
        result_holder['demotions'] = demotions
        return updated_list

    commit_message = f"result: {parsed.player_name} -> {parsed.kit} ({parsed.tier_after})"
    github_storage.update_players_file(GH_REPO, GH_TOKEN, mutate, commit_message)

    overall_tier = result_holder['overall_tier']
    demotions = result_holder['demotions']

    topic = determine_topic(parsed.tier_after)

    card_text = build_result_card(
        player_name=parsed.player_name,
        kit=parsed.kit,
        tier_before=parsed.tier_before,
        tier_after=parsed.tier_after,
        duels=parsed.duels,
        comment=parsed.comment,
        overall_tier=overall_tier,
        is_high_topic=(topic == 'high'),
    )
    thread_id = HIGH_RESULTS_THREAD_ID if topic == 'high' else RESULTS_THREAD_ID

    send_kwargs = {"chat_id": RESULTS_CHAT_ID, "text": card_text}
    if thread_id is not None:
        send_kwargs["message_thread_id"] = thread_id

    bot.send_message(**send_kwargs)

    # Публикуем отдельную карточку для каждого штрафного автопонижения,
    # произошедшего в результате этого сообщения (может быть 0 или
    # несколько - в многодуэльном тесте может понизиться и игрок, и
    # несколько разных оппонентов одновременно)
    for demotion in demotions:
        demotion_card = build_penalty_demotion_card(
            player_name=demotion['player_name'],
            kit=demotion['kit'],
            old_tier=demotion['old_tier'],
            new_tier=demotion['new_tier'],
            overall_tier=demotion['overall_tier'],
        )
        demotion_topic = determine_topic(demotion['new_tier'])
        demotion_thread_id = HIGH_RESULTS_THREAD_ID if demotion_topic == 'high' else RESULTS_THREAD_ID

        demotion_kwargs = {"chat_id": RESULTS_CHAT_ID, "text": demotion_card}
        if demotion_thread_id is not None:
            demotion_kwargs["message_thread_id"] = demotion_thread_id

        bot.send_message(**demotion_kwargs)


def handle_processing_error(exc):
    """Вызывается очередью, если process_result упал с исключением."""
    print(f"[result_queue] Ошибка обработки результата: {exc}")


# ==========================================
# TELEGRAM: приём сообщений из группы тестеров
# ==========================================

def is_in_source_topic(message) -> bool:
    if message.chat.id != SOURCE_CHAT_ID:
        return False
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
