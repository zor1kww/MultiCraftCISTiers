# -*- coding: utf-8 -*-
"""
Расчёт Эло для PvP-дуэлей MultiCraft.

Вся механика зафиксирована в переписке с администратором ("саша 999") и
не содержит открытых вопросов:
  - Эло ведётся ОТДЕЛЬНО по каждому киту (не общее на игрока).
  - Старт нового игрока на ките - 1000 (= HT5).
  - Тир (HT1..LT5) НЕ хранится - всегда вычисляется из эло функцией
    get_tier(). Если диапазоны тиров позже поменяются, это один файл,
    а не рассинхронизированные копии в БД.
  - K-фактор берётся ОТДЕЛЬНО для каждого игрока, по ЕГО тиру до матча
    (у новичка в одном матче может быть K=40, у топа-соперника K=8).
  - Множитель антиабуза M - общий для обоих игроков пары (это свойство
    пары+кита+окна, а не отдельного игрока). Эта функция принимает его
    уже готовым - подсчёт по БД (сколько дуэлей пары в ките за
    последние 2 часа ДО этого матча) делает вызывающий код, здесь
    только применение.
  - Округление - математическое (round half up), не банковское.
  - Проигравший никогда не уходит в минус: теряет не больше, чем у
    него есть. Победитель получает ровно столько же, сколько реально
    потерял проигравший (не изначальную дельту "из воздуха").
  - Ничьих нет: всегда есть явный победитель и проигравший, по смерти
    или по автопоражению (не вернулся за 3 минуты) - при автопоражении
    формула ровно та же, без исключений.
"""

import math
from dataclasses import dataclass


# ==========================================
# ТИРЫ И K-ФАКТОР
# ==========================================

# От сильного к слабому - порядок важен для некоторых потребителей
# (например, при выводе списка тиров), сама привязка идёт по диапазону.
TIER_TABLE = [
    # (нижняя граница эло, тир, K)
    (2250, "HT1", 8),
    (2100, "MT1", 10),
    (1950, "LT1", 12),
    (1850, "HT2", 12),
    (1750, "MT2", 14),
    (1650, "LT2", 16),
    (1550, "HT3", 16),
    (1450, "MT3", 18),
    (1350, "LT3", 20),
    (1250, "HT4", 22),
    (1150, "MT4", 24),
    (1050, "LT4", 28),
    (1000, "HT5", 32),
    (950, "MT5", 36),
    (0, "LT5", 40),
]

STARTING_ELO = 1000  # = HT5

# Бракеты антиабуза: (макс. число ПРЕДЫДУЩИХ дуэлей пары в ките за окно
# 2 часа -> множитель). Текущий матч в счётчик не входит - считаются
# только уже завершённые до него. Первая дуэль пары => count=0 => M=1.0.
ANTI_ABUSE_BRACKETS = [
    (4, 1.00),
    (8, 0.50),
    (12, 0.25),
    (16, 0.10),
]
ANTI_ABUSE_WINDOW_HOURS = 2


def get_tier(elo: float) -> str:
    """Тир по эло. Эло ниже 0 быть не должно (см. пол ниже), но на
    всякий случай отрицательные значения тоже попадают в LT5."""
    for lower_bound, tier, _k in TIER_TABLE:
        if elo >= lower_bound:
            return tier
    return "LT5"  # недостижимо при TIER_TABLE[-1] == (0, "LT5", ...), но на всякий случай


def get_k_factor(elo: float) -> int:
    """K-фактор по эло (через тир)."""
    for lower_bound, _tier, k in TIER_TABLE:
        if elo >= lower_bound:
            return k
    return TIER_TABLE[-1][2]


def anti_abuse_multiplier(prior_duels_count: int) -> float:
    """
    M по числу УЖЕ СОСТОЯВШИХСЯ дуэлей этой пары в этом ките за
    скользящее окно 2 часа, ДО текущего матча (текущий не считается).

    count=0..4   -> 1.00 (дуэли 1-5 по счёту)
    count=5..8   -> 0.50 (дуэли 6-9)
    count=9..12  -> 0.25 (дуэли 10-13)
    count=13..16 -> 0.10 (дуэли 14-17)
    count>=17    -> 0.00
    """
    if prior_duels_count < 0:
        raise ValueError("prior_duels_count не может быть отрицательным")
    for max_count, multiplier in ANTI_ABUSE_BRACKETS:
        if prior_duels_count <= max_count:
            return multiplier
    return 0.0


def expected_score(elo_self: float, elo_opponent: float) -> float:
    """Ожидание победы (0..1) по стандартной формуле Эло."""
    return 1.0 / (1.0 + 10 ** ((elo_opponent - elo_self) / 400))


def _round_half_up(value: float) -> int:
    """Математическое округление (round half up), не банковское.
    round(9.5) должно дать 10, а не 10 через "round to even" Python'а
    (round(9.5) в Python == 10 случайно, но round(2.5) == 2 - поэтому
    не полагаемся на встроенный round и делаем явно)."""
    return math.floor(value + 0.5) if value >= 0 else -math.floor(-value + 0.5)


@dataclass
class MatchResult:
    """Результат применения матча к обоим игрокам."""
    winner_elo_before: float
    winner_elo_after: float
    winner_delta: int          # фактически начислено победителю (= delta_actual)

    loser_elo_before: float
    loser_elo_after: float
    loser_delta: int           # фактически списано у проигравшего (= delta_actual, положительное число)

    k_winner: int
    k_loser: int
    m_factor: float
    expected_winner: float     # ожидание победы победителя ДО матча (для аудита)
    capped: bool                # True, если делта была урезана полом в 0 у проигравшего


def compute_match(elo_winner: float, elo_loser: float, prior_duels_count: int) -> MatchResult:
    """
    Применяет один матч. Ничьих нет - вызывающий код уже знает, кто
    победитель, а кто проигравший (по смерти либо по автопоражению).

    elo_winner / elo_loser - эло ОБОИХ до матча, в этом ките.
    prior_duels_count - число дуэлей этой же пары в этом ките за окно
    2 часа ДО этого матча (не считая его самого).

    К победителя и К проигравшего берутся КАЖДЫЙ ПО СВОЕМУ эло до
    матча и, как следствие, обычно РАЗНЫЕ - так же разные и исходные
    дельты (delta_winner, delta_loser), сумма эло в системе НЕ обязана
    сохраняться (как в ФИДЕ). Проверено на контрольном примере
    (Steve 1400 K=20 проигрывает Alex 1200 K=24, M=0.5):
    delta_Alex(победитель)=+9, delta_Steve(проигравший)=-2 - две разные
    величины, не одна общая.

    Исключение - пол по нулю: если у проигравшего не хватает эло,
    чтобы потерять свою полную дельту, он теряет сколько есть, и в
    этом (и только в этом) случае победитель получает ровно столько
    же, сколько проигравший реально потерял, а не свою исходную
    дельту - чтобы не создавать эло "из воздуха".
    """
    k_winner = get_k_factor(elo_winner)
    k_loser = get_k_factor(elo_loser)
    m = anti_abuse_multiplier(prior_duels_count)

    e_winner = expected_score(elo_winner, elo_loser)
    e_loser = expected_score(elo_loser, elo_winner)  # = 1 - e_winner, считаем явно для аудита

    delta_winner = _round_half_up(k_winner * (1 - e_winner) * m)
    delta_loser = _round_half_up(k_loser * (1 - e_loser) * m)

    # Пол: проигравший не может потерять больше, чем у него есть.
    available = math.floor(elo_loser)
    loser_actual = min(delta_loser, available) if available >= 0 else 0
    loser_actual = max(0, loser_actual)
    capped = loser_actual < delta_loser

    # Обычный случай - у каждого своя дельта. Только если пол реально
    # сработал (проигравшему срезали потерю) - победитель получает
    # ровно столько же, сколько проигравший фактически потерял.
    winner_actual = loser_actual if capped else delta_winner

    winner_after = elo_winner + winner_actual
    loser_after = max(0.0, elo_loser - loser_actual)

    return MatchResult(
        winner_elo_before=elo_winner,
        winner_elo_after=winner_after,
        winner_delta=winner_actual,
        loser_elo_before=elo_loser,
        loser_elo_after=loser_after,
        loser_delta=loser_actual,
        k_winner=k_winner,
        k_loser=k_loser,
        m_factor=m,
        expected_winner=e_winner,
        capped=capped,
    )
