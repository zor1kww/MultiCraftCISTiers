# -*- coding: utf-8 -*-
"""
Чистая бизнес-логика тиров, дат и текста карточек результата.
Никаких обращений к Telegram/GitHub - только вычисления, чтобы можно
было протестировать независимо от сети и ботового рантайма.
"""

from datetime import date, datetime, timedelta
from bot_config import (
    TIER_ORDER, RETIRED_ELIGIBLE_TIERS, TIER_WEIGHTS, REVERSE_WEIGHTS,
    HIGH_RESULT_TIERS, RETIRED_AUTO_DAYS, PENALTY_DEMOTION_THRESHOLD
)


def today_str() -> str:
    return date.today().isoformat()


def is_date_expired(date_str: str, days: int = RETIRED_AUTO_DAYS) -> bool:
    """True, если с указанной даты прошло больше `days` дней."""
    if not date_str:
        return False
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return False
    return (date.today() - d).days > days


def tier_rank_index(tier: str):
    """Индекс тира в TIER_ORDER (0 = старший). None, если тир неизвестен/Unranked."""
    try:
        return TIER_ORDER.index(tier)
    except ValueError:
        return None


def compare_tiers(tier_a: str, tier_b: str) -> int:
    """
    Сравнивает два тира по "силе". Возвращает:
      >0 если tier_a старше tier_b (выше рангом)
      <0 если tier_a младше tier_b
       0 если равны или один из них не входит в TIER_ORDER (Unranked и т.п.)
    Использует TIER_WEIGHTS, т.к. он уже 1-в-1 задаёт порядок числом.
    """
    wa = TIER_WEIGHTS.get(tier_a)
    wb = TIER_WEIGHTS.get(tier_b)
    if wa is None or wb is None:
        return 0
    return wa - wb


def is_retired_eligible(tier: str) -> bool:
    """Может ли этот тир вообще иметь статус Retired (правило: HT3 и выше)."""
    return tier in RETIRED_ELIGIBLE_TIERS


def compute_is_retired(tier: str, date_str: str, manual_retired: bool) -> bool:
    """
    Итоговый Retired-статус кита: ручной ИЛИ просроченная дата,
    но только если тир вообще имеет право на Retired (HT3+).
    Совпадает 1-в-1 с parseTierInfo() на фронте.
    """
    if not is_retired_eligible(tier):
        return False
    return bool(manual_retired) or is_date_expired(date_str)


def calculate_overall_tier(player_tiers: dict):
    """
    Средний тир игрока по всем его китам. Retired-киты УЧАСТВУЮТ
    в расчёте наравне с обычными (так же, как на фронте) - Retired
    влияет только на видимость в списке, не на среднее.
    player_tiers - словарь в новом формате: {kit: {tier, date, retired}}
    Возвращает (overall_tier_str, tests_count).
    """
    total_weight = 0
    count = 0

    for kit_name, tier_val in player_tiers.items():
        if isinstance(tier_val, dict):
            tier_str = tier_val.get('tier', 'Unranked')
        else:
            # обратная совместимость со старым строковым форматом
            tier_str = str(tier_val)
            if tier_str.startswith('R') and len(tier_str) > 1 and tier_str[1:] in TIER_ORDER:
                tier_str = tier_str[1:]

        if tier_str in TIER_WEIGHTS:
            total_weight += TIER_WEIGHTS[tier_str]
            count += 1

    if count == 0:
        return "Unranked", 0

    avg_weight = round(total_weight / count)
    overall = REVERSE_WEIGHTS.get(avg_weight, "Unranked")
    return overall, count


def determine_topic(final_tier: str) -> str:
    """
    Определяет топик по ИТОГОВОМУ тиру (полученный ранг), без учёта
    тира "до". Возвращает 'high' или 'normal'.
    """
    return 'high' if final_tier in HIGH_RESULT_TIERS else 'normal'


def format_full_tier_name(tier: str) -> str:
    """'HT3' -> 'High Tier 3', 'LT4' -> 'Low Tier 4', 'Unranked' -> 'Unranked'."""
    if tier == "Unranked" or len(tier) < 3:
        return tier
    prefix = "High Tier" if tier[0] == 'H' else "Low Tier"
    number = tier[2:]
    return f"{prefix} {number}"


def verb_for_change(tier_before: str, tier_after: str, is_new_player_kit: bool) -> str:
    """
    Подбирает глагол для заголовка обычного результата (не высокого теста).
    Высокие тесты используют отдельную фразу "проходит"/"проваливает" -
    эта функция для топика "Результаты".
    """
    if is_new_player_kit or tier_before is None or tier_before == "Unranked":
        return "получает"
    diff = compare_tiers(tier_after, tier_before)
    if diff > 0:
        return "повышается до"
    elif diff < 0:
        return "понижается до"
    else:
        return "закрепляется на"


def tester_display_name(tester_name: str) -> str:
    """
    Формирует отображаемое имя тестера для карточки. В новой архитектуре
    тестер identифицируется просто по имени из шаблонного сообщения
    (поле "Тестер:"), а не по Telegram user_id - никакого маппинга
    на реальный @username не требуется.
    """
    return tester_name


def build_high_test_card(player_name, region, kit, tier_before, tier_after,
                          score_tester, score_player, winner, tester_display,
                          comment, overall_tier, tests_count):
    """
    Карточка для топика "Высокие результаты" (полученный тир HT3-HT1).

    Топик определяется исключительно по tier_after (см. determine_topic) -
    если тест провален и тир не изменился, результат попадает в топик
    "Результаты" через build_normal_result_card, а не сюда. Поэтому
    здесь ВСЕГДА действие "проходит" - формулировки "проваливает" не
    существует в этой карточке в принципе.
    """
    full_tier_name = format_full_tier_name(tier_after)

    lines = []
    lines.append(f"{player_name} [{region}] проходит {kit} {full_tier_name} тест")
    lines.append("")

    if tier_before and tier_before != "Unranked" and tier_before != tier_after:
        lines.append(f"Предыдущий ранг: {format_full_tier_name(tier_before)}")
        lines.append("")

    lines.append("Поединки:")
    lines.append(f"▸ Против {tester_display}")
    lines.append(f"{player_name}   {score_player}:{score_tester}   {tester_display}")
    lines.append("")

    lines.append(f"Тир-тестер: {tester_display}")
    lines.append(f"Комментарий: {comment if comment else '—'}")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(f"Текущий средний ранг: {overall_tier} [Тестов: {tests_count}]")

    return "\n".join(lines)


def build_normal_result_card(player_name, region, kit, tier_before, tier_after,
                              is_new_player_kit, tester_display, comment,
                              overall_tier, tests_count):
    """
    Карточка для топика "Результаты" (обычные результаты, LT5-LT3).
    """
    verb = verb_for_change(tier_before, tier_after, is_new_player_kit)
    full_tier_name = format_full_tier_name(tier_after)

    lines = []
    lines.append(f"{player_name} [{region}] {verb} {kit} {full_tier_name}")
    lines.append("")
    lines.append(f"Тир-тестер: {tester_display}")
    if comment:
        lines.append(f"Комментарий: {comment}")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(f"Текущий средний ранг: {overall_tier} [Тестов: {tests_count}]")

    return "\n".join(lines)


def build_match_history_entry(kit, tester_name, player_name, tier_before, tier_after,
                               score_tester, score_player, winner, comment, test_date=None):
    """
    Собирает запись для matchHistory игрока (лог дуэлей на сайте).
    Хранится в самом объекте игрока, каждый обработанный результат
    (включая обычные LT5-LT3) добавляет сюда одну запись.
    """
    return {
        "date": test_date or today_str(),
        "kit": kit,
        "tester": tester_name,
        "tierBefore": tier_before,
        "tierAfter": tier_after,
        "scoreTester": score_tester,
        "scorePlayer": score_player,
        "winner": winner,       # "tester" или "player"
        "comment": comment,     # может быть None
    }


def build_tier_object(tier: str, retired: bool = False, test_date: str = None) -> dict:
    """Собирает объект тира в новом формате для записи в players.js."""
    return {
        "tier": tier,
        "date": test_date or today_str(),
        "retired": bool(retired)
    }


def build_penalty_demotion_card(player_name, region, kit, old_tier, new_tier,
                                 overall_tier, tests_count):
    """
    Карточка автоматического понижения из-за накопленных штрафных очков
    (см. penalty_logic.py). Публикуется по тому же правилу топика, что
    и обычные результаты (determine_topic(new_tier)), но с явным
    указанием причины, чтобы не выглядело как обычный проваленный тест.
    """
    full_old = format_full_tier_name(old_tier)
    full_new = format_full_tier_name(new_tier)

    lines = []
    lines.append(f"{player_name} [{region}] понижается до {kit} {full_new}")
    lines.append("")
    lines.append(f"Причина: накоплено {PENALTY_DEMOTION_THRESHOLD:g} штрафных очка по этому киту")
    lines.append(f"Было: {full_old} → Стало: {full_new}")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(f"Текущий средний ранг: {overall_tier} [Тестов: {tests_count}]")

    return "\n".join(lines)
