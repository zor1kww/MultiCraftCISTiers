# -*- coding: utf-8 -*-
"""
Система штрафных очков (только для HT3+ тестов, топик "Высокие результаты").

Правила (см. документ с правилами высокого теста):
  - Штраф получает ТОЛЬКО проигравший.
  - Тестируемый игрок получает штраф всегда, когда проигрывает
    (winner == "tester") - штраф пишется на его тир ДО теста
    (Предыдущий ранг), на этом же ките.
  - Тестер получает штраф, только если он проигрывает
    (winner == "player") И его собственный тир на этом ките
    равен или выше тира игрока до теста. Если тестера нет в базе
    или он Unranked на этом ките - считается ниже любого ранга,
    штраф не даётся (безопасный дефолт при недостатке данных).
  - Размер штрафа зависит от ФОРМАТА МАТЧА (FT2/FT4/FT6 - см.
    bot_config.FT2_KITS/FT6_KITS) и от точного счёта проигравшего.
  - При достижении суммарных штрафных очков по киту >= 2.0 - игрок
    (тестируемый ИЛИ тестер, в зависимости от того, кто накопил)
    автоматически понижается на 1 ступень по TIER_ORDER на этом ките,
    очки по этому киту сбрасываются в 0.
  - Раз в месяц ВСЕ штрафные очки всех игроков обнуляются полностью
    (см. reset_all_penalties ниже - вызывается по расписанию, не
    привязано к конкретному результату).
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
        # Каждый элемент: {"player_name": str, "kit": str, "penalty_added": float,
        #                   "demoted": bool, "old_tier": str|None, "new_tier": str|None}
        self.entries = []

    def add(self, player_name, kit, penalty_added, demoted=False, old_tier=None, new_tier=None):
        self.entries.append({
            "player_name": player_name,
            "kit": kit,
            "penalty_added": penalty_added,
            "demoted": demoted,
            "old_tier": old_tier,
            "new_tier": new_tier,
        })

    def has_any_penalty(self) -> bool:
        return len(self.entries) > 0

    def demotions(self):
        return [e for e in self.entries if e["demoted"]]


def apply_penalties_for_result(kit, tester_name, player_name, tier_before_player,
                                score_tester, score_player, winner,
                                get_player_tier_fn):
    """
    Вычисляет штрафы для одной дуэли (не мутирует базу - только считает).

    get_player_tier_fn(player_name, kit) -> str|None - функция для получения
    текущего тира игрока (тестера) на данном ките из базы. Передаётся
    снаружи, чтобы этот модуль не был завязан на формат players_list.

    Возвращает PenaltyResult с записями ТОЛЬКО для тех, кто реально
    получает штраф в этой дуэли (проигравший, и только если условия
    штрафа выполнены).

    ВАЖНО: возвращённые penalty_added - это штраф ЗА ЭТУ дуэль. Порог
    демоции (>=2.0) проверяется снаружи, после того как этот штраф
    суммирован с уже накопленными очками игрока по этому киту - эта
    функция не знает текущей суммы, только вычисляет прирост.
    """
    result = PenaltyResult()

    loser_score = score_tester if winner == "player" else score_player
    penalty = calculate_penalty(kit, loser_score)

    if penalty <= 0:
        return result

    if winner == "tester":
        # Тестируемый игрок проиграл - штраф всегда
        result.add(player_name, kit, penalty)
    else:
        # winner == "player" - тестер проиграл, штраф только если тестер
        # равного/выше ранга, чем игрок ДО теста
        tester_tier = get_player_tier_fn(tester_name, kit)
        if tester_tier and is_equal_or_higher_rank(tester_tier, tier_before_player):
            result.add(tester_name, kit, penalty)

    return result
