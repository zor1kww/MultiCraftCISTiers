# -*- coding: utf-8 -*-
"""
Система штрафных очков (только для HT3+ тестов, топик "Высокие результаты").

Правила (см. документ с правилами высокого теста, обновлено под v4 -
терминология "Оппонент" вместо "Тестер", симметричный штраф):
  - Штраф получает ТОЛЬКО проигравший СВОЮ дуэль, и только если он
    равного/выше ранга, чем противоположная сторона ДО теста.
    Правило симметрично: игрок и оппонент штрафуются по одному и тому
    же принципу, никакой особой роли "тестер" больше нет.
  - Штраф пишется на тир проигравшего НА МОМЕНТ ДО этого результата
    (тир оппонента - его текущий тир в базе; тир игрока - его
    "Предыдущий ранг" из шаблона).
  - Если проигравшего нет в базе или он Unranked на этом ките -
    считается ниже любого валидного тира, штраф не даётся (безопасный
    дефолт при недостатке данных).
  - Размер штрафа зависит от ФОРМАТА МАТЧА (FT2/FT4/FT6 - см.
    bot_config.FT2_KITS/FT6_KITS) и от точного счёта проигравшего в
    конкретной дуэли (не агрегата - штраф считается ПО КАЖДОЙ дуэли
    отдельно, это важно для многодуэльного HT1-теста).
  - При достижении суммарных штрафных очков по киту >= 2.0 - игрок
    автоматически понижается на 1 ступень по TIER_ORDER на этом ките,
    очки по этому киту сбрасываются в 0.
  - Раз в месяц (точнее - через 30 дней с даты первого начисления в
    текущем цикле) все штрафные очки по этому циклу истекают - см.
    is_penalty_cycle_expired/effective_penalty_points.

Отдельно от штрафов: оппонент теперь тоже может ПОВЫШАТЬСЯ, если он
выиграл дуэль - но это не штрафной механизм, это обрабатывается в
main.py напрямую (оппонент, который выиграл и претендует на новый ранг,
просто указывается в поле "Игрок:" следующего результата - тестеры сами
решают, кто в каком сообщении является "игроком, тестируемым на ранг").
"""

from datetime import date, datetime
from bot_config import (
    TIER_ORDER, TIER_WEIGHTS, FT2_KITS, FT6_KITS, PENALTY_DEMOTION_THRESHOLD,
    PENALTY_EXPIRY_DAYS
)


# ==========================================
# ТАБЛИЦЫ ШТРАФОВ ПО ФОРМАТУ МАТЧА
# ==========================================

# Ключ - счёт проигравшего (сколько раундов взял проигравший), значение - штраф.
# Победитель в каждом формате всегда берёт ровно "побед_до" раундов.
PENALTY_TABLE_FT2 = {1: 1.0, 0: 2.0}
PENALTY_TABLE_FT4 = {3: 0.0, 2: 1.0, 1: 1.5, 0: 2.0}
PENALTY_TABLE_FT6 = {5: 0.0, 4: 0.4, 3: 0.8, 2: 1.2, 1: 1.6, 0: 2.0}


def match_format_for_kit(kit: str) -> int:
    """Возвращает 2, 4 или 6 - до скольких побед идёт матч на этом ките."""
    if kit in FT2_KITS:
        return 2
    if kit in FT6_KITS:
        return 6
    return 4


def penalty_table_for_kit(kit: str) -> dict:
    fmt = match_format_for_kit(kit)
    if fmt == 2:
        return PENALTY_TABLE_FT2
    if fmt == 6:
        return PENALTY_TABLE_FT6
    return PENALTY_TABLE_FT4


def calculate_penalty(kit: str, loser_score: int) -> float:
    """
    Возвращает штраф (0.0-2.0) по счёту проигравшего в данном ките.
    loser_score - число раундов, которое взял проигравший (не победитель).
    Если счёт не входит в допустимые для формата этого кита (например
    прислали 3:1 для FT2, где такого быть не может) - возвращает 0.0
    и не начисляет штраф (защита от мусорных данных, не должно
    происходить при корректном парсинге, но на всякий случай).
    """
    table = penalty_table_for_kit(kit)
    return table.get(loser_score, 0.0)


def tier_weight_or_unranked(tier: str) -> int:
    """Вес тира для сравнения рангов. Unranked/неизвестный тир = 0 (самый низкий)."""
    return TIER_WEIGHTS.get(tier, 0)


def is_equal_or_higher_rank(tier_a: str, tier_b: str) -> bool:
    """True, если tier_a равен или старше tier_b по весу."""
    return tier_weight_or_unranked(tier_a) >= tier_weight_or_unranked(tier_b)


def next_tier_down(tier: str):
    """Возвращает следующую (более низкую) ступень по TIER_ORDER.
    None, если tier уже LT5 (ниже некуда) или не входит в TIER_ORDER."""
    try:
        idx = TIER_ORDER.index(tier)
    except ValueError:
        return None
    if idx + 1 >= len(TIER_ORDER):
        return None  # уже на самой низкой ступени (LT5)
    return TIER_ORDER[idx + 1]


def is_penalty_cycle_expired(first_penalty_date: str, days: int = PENALTY_EXPIRY_DAYS) -> bool:
    """True, если с даты первого начисления в текущем цикле штрафов
    прошло больше `days` дней - весь накопленный штраф по этому циклу
    должен считаться истёкшим (обнулённым)."""
    if not first_penalty_date:
        return False
    try:
        d = datetime.strptime(first_penalty_date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return False
    return (date.today() - d).days > days


def effective_penalty_points(penalty_entry: dict) -> float:
    """
    Возвращает актуальные (не истёкшие) штрафные очки по одному киту.
    penalty_entry - {"points": float, "firstPenaltyDate": str} или None.
    Используется как "ленивая" проверка перед начислением нового штрафа
    (в боте) и для отображения на сайте (порт этой же логики в JS) -
    сама запись в базе не меняется этой функцией, только чтение.
    """
    if not penalty_entry:
        return 0.0
    if is_penalty_cycle_expired(penalty_entry.get("firstPenaltyDate")):
        return 0.0
    return penalty_entry.get("points", 0.0)


def add_penalty_to_entry(penalty_entry: dict, added: float, today: str) -> dict:
    """
    Возвращает НОВЫЙ penalty_entry с добавленным штрафом added, учитывая
    истечение предыдущего цикла:
      - если penalty_entry пуст/None ИЛИ его цикл истёк - начинается
        новый цикл: points = added, firstPenaltyDate = today
      - иначе - points увеличивается на added, firstPenaltyDate НЕ меняется
    """
    if not penalty_entry or is_penalty_cycle_expired(penalty_entry.get("firstPenaltyDate")):
        return {"points": added, "firstPenaltyDate": today}
    return {
        "points": penalty_entry.get("points", 0.0) + added,
        "firstPenaltyDate": penalty_entry.get("firstPenaltyDate", today),
    }


class PenaltyResult:
    """Описывает, что нужно применить к базе игроков в результате штрафов
    одной дуэли. Само применение (запись в players_list) делается снаружи
    (в main.py), этот модуль только вычисляет, что должно произойти."""

    def __init__(self):
        # Каждый элемент: {"player_name": str, "kit": str, "penalty_added": float}
        self.entries = []

    def add(self, player_name, kit, penalty_added):
        self.entries.append({
            "player_name": player_name,
            "kit": kit,
            "penalty_added": penalty_added,
        })

    def has_any_penalty(self) -> bool:
        return len(self.entries) > 0


def apply_penalty_for_duel(kit, player_name, opponent_name, tier_before_player,
                            score_player, score_opponent, winner, get_player_tier_fn):
    """
    Вычисляет штраф для ОДНОЙ дуэли (не мутирует базу - только считает).
    Симметрично: штрафуется тот, кто проиграл ЭТУ дуэль, если он
    равного/выше ранга, чем противоположная сторона.

    get_player_tier_fn(player_name, kit) -> str|None - функция для получения
    текущего тира игрока из базы (для оппонента - его текущий тир;
    для игрока используется tier_before_player напрямую, т.к. это его
    тир ДО результата, а не текущий в базе, который может быть уже
    обновлён к моменту вызова).

    Возвращает PenaltyResult с записью ТОЛЬКО для того, кто реально
    получает штраф (может быть 0 или 1 запись за одну дуэль).
    """
    result = PenaltyResult()

    loser_score = score_player if winner == "opponent" else score_opponent
    penalty = calculate_penalty(kit, loser_score)

    if penalty <= 0:
        return result

    if winner == "opponent":
        # Игрок проиграл эту дуэль - штрафуется, если оппонент был
        # равного/выше ранга, чем игрок ДО теста
        opponent_tier = get_player_tier_fn(opponent_name, kit)
        if opponent_tier and is_equal_or_higher_rank(opponent_tier, tier_before_player):
            result.add(player_name, kit, penalty)
    else:
        # winner == "player" - оппонент проиграл эту дуэль - штрафуется,
        # если ОН был равного/выше ранга, чем игрок ДО теста (тот же
        # критерий силы соперника, симметрично)
        opponent_tier = get_player_tier_fn(opponent_name, kit)
        if opponent_tier and is_equal_or_higher_rank(opponent_tier, tier_before_player):
            result.add(opponent_name, kit, penalty)

    return result

