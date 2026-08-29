# -*- coding: utf-8 -*-
"""
Парсер шаблонного сообщения из закрытой группы (v4).

Шаблон, ОДНОДУЭЛЬНЫЙ случай (обычные переходы, включая обычные
результаты и одиночные HT3+ тесты LT3->HT3, HT3->LT2, LT2->HT2,
HT2->LT1):

    Оппонент: zor1kkqwix
    Игрок: Prosto_oleg100-7
    Кит: Emerald
    Регион: RU
    Предыдущий ранг: LT5
    Полученный ранг: LT3
    Счёт: 4:2 в пользу оппонента
    Комментарий: (необязательно)

Шаблон, МНОГОДУЭЛЬНЫЙ случай (HT1-тест LT1->HT1, несколько соперников):

    Оппонент: zor1kkqwix, -BaCk-, -999-
    Игрок: Prosto_oleg100-7
    Кит: Emerald
    Регион: RU
    Предыдущий ранг: LT3
    Полученный ранг: HT1
    Счёт: 4:2, 4:1, 4:3
    Комментарий: (необязательно)

В многодуэльном случае "Оппонент:" и "Счёт:" - списки через запятую,
сопоставляются ПОЗИЦИОННО (N-й оппонент <-> N-я пара чисел). В счёте
многодуэльного случая первое число всегда принадлежит ИГРОКУ (не нужно
"в пользу X" - это ясно из позиции). Однодуэльный случай использует
явное "в пользу оппонента/игрока".

"Игрок:" - это тот, кто фактически тестируется на новый ранг (кто бы
им ни был - раньше это был жёстко "тестируемый", теперь им может стать
и оппонент, если он выиграл и претендует на повышение - имя победителя
просто пишется в поле "Игрок:").

Обязательные поля: Оппонент, Игрок, Кит, Регион, Предыдущий ранг,
Полученный ранг, Счёт. Если хотя бы одно из них не найдено - сообщение
считается НЕ результатом (обычное обсуждение в топике) и игнорируется
без ошибки (см. looks_like_result).
"""

import re
from dataclasses import dataclass
from typing import Optional

from bot_config import VALID_KITS, REGIONS, TIER_ORDER


REQUIRED_FIELD_LABELS = {
    "opponent": ["оппонент", "тестер"],
    "player": ["игрок"],
    "kit": ["кит"],
    "region": ["регион"],
    "tier_before": ["предыдущий ранг"],
    "tier_after": ["полученный ранг"],
    "score": ["счёт", "счет"],
}
OPTIONAL_FIELD_LABELS = {
    "comment": ["комментарий"],
}

# Тир может быть написан в любом регистре (ht3, Ht3, HT3) - нормализуем
_TIER_LOOKUP = {t.upper(): t for t in TIER_ORDER}
_TIER_LOOKUP["UNRANKED"] = "Unranked"

# Кит и регион ищем по точному совпадению без учёта регистра
_KIT_LOOKUP = {k.lower(): k for k in VALID_KITS}
_REGION_LOOKUP = {r.lower(): r for r in REGIONS}

# Однодуэльный счёт: "4:2 в пользу оппонента" / "4:2 в пользу игрока".
# "тестера" принимается как устаревший синоним "оппонента" - часть
# тестеров ещё пишет по старому шаблону, привыкать заново не обязаны.
SINGLE_SCORE_PATTERN = re.compile(
    r"^\s*(\d{1,2})\s*[:\-]\s*(\d{1,2})\s+в\s+пользу\s+(оппонента|тестера|игрока)\s*$",
    re.IGNORECASE
)
# Многодуэльный счёт (одна пара из списка через запятую): "4:2" без "в пользу"
MULTI_SCORE_ITEM_PATTERN = re.compile(r"^\s*(\d{1,2})\s*[:\-]\s*(\d{1,2})\s*$")


@dataclass
class Duel:
    opponent: str
    score_player: int
    score_opponent: int
    winner: str  # "player" или "opponent"


@dataclass
class ParsedResult:
    player_name: str
    kit: str
    region: str
    tier_before: str
    tier_after: str
    duels: list            # список Duel; 1 элемент для однодуэльного, N для HT1
    is_multi_duel: bool
    winner: str             # ИТОГ всего теста: "player" или "opponent"
    score_player: int       # агрегат: сумма выигранных дуэлей игроком
    score_opponent: int     # агрегат: сумма выигранных дуэлей оппонентами
    comment: Optional[str]
    raw_text: str


class ParseError(Exception):
    """Сообщение похоже на результат (есть хотя бы одна метка полей),
    но не хватает обязательных полей или значение некорректно.
    В отличие от 'не результат вовсе' (тогда возвращается None без
    исключения), это сигнал автору сообщения, что он почти написал
    результат, но ошибся - стоит показать ему причину."""
    def __init__(self, message: str, missing_fields=None):
        super().__init__(message)
        self.missing_fields = missing_fields or []


def _extract_field(text: str, labels: list) -> Optional[str]:
    """Ищет строку вида 'Метка: значение' (без учёта регистра метки).
    Возвращает значение (обрезанное) или None, если метка не найдена."""
    for label in labels:
        pattern = re.compile(
            rf"^\s*{re.escape(label)}\s*:\s*(.*?)\s*$",
            re.IGNORECASE | re.MULTILINE
        )
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None


def looks_like_result(text: str) -> bool:
    """Быстрая проверка: есть ли в тексте хотя бы 2 из обязательных меток.
    Используется, чтобы отличить 'это явно не результат' (полностью
    игнорируем, никакой ошибки) от 'похоже на результат, но что-то не так'
    (стоит сообщить об ошибке)."""
    found = 0
    for labels in REQUIRED_FIELD_LABELS.values():
        if _extract_field(text, labels) is not None:
            found += 1
    return found >= 2


def _split_comma_list(value: str) -> list:
    return [item.strip() for item in value.split(',') if item.strip()]


def parse_result_message(text: str) -> Optional[ParsedResult]:
    """
    Пытается распарсить текст сообщения как результат теста.

    Возвращает ParsedResult при успехе.
    Возвращает None, если сообщение явно не похоже на результат
    (меньше 2 меток найдено вообще) - значит это обычное обсуждение,
    молча игнорируем.
    Бросает ParseError, если сообщение ПОХОЖЕ на результат (2+ метки),
    но не хватает обязательных полей или значения некорректны.
    """
    if not looks_like_result(text):
        return None

    missing = []
    values = {}

    for field_key, labels in REQUIRED_FIELD_LABELS.items():
        value = _extract_field(text, labels)
        if not value:
            missing.append(field_key)
        else:
            values[field_key] = value

    if missing:
        raise ParseError(f"Не найдены обязательные поля: {', '.join(missing)}", missing_fields=missing)

    # --- Валидация и нормализация базовых значений ---

    kit_raw = values["kit"]
    kit = _KIT_LOOKUP.get(kit_raw.lower())
    if kit is None:
        raise ParseError(f"Неизвестный кит: {kit_raw!r}. Допустимые: {', '.join(VALID_KITS)}")

    region_raw = values["region"]
    region = _REGION_LOOKUP.get(region_raw.lower())
    if region is None:
        raise ParseError(f"Неизвестный регион: {region_raw!r}. Допустимые: {', '.join(REGIONS)}")

    tier_before_raw = values["tier_before"]
    tier_before = _TIER_LOOKUP.get(tier_before_raw.upper())
    if tier_before is None:
        raise ParseError(f"Неизвестный 'Предыдущий ранг': {tier_before_raw!r}")

    tier_after_raw = values["tier_after"]
    tier_after = _TIER_LOOKUP.get(tier_after_raw.upper())
    if tier_after is None:
        raise ParseError(f"Неизвестный 'Полученный ранг': {tier_after_raw!r}")

    comment = _extract_field(text, OPTIONAL_FIELD_LABELS["comment"]) or None
    player_name = values["player"]

    opponents = _split_comma_list(values["opponent"])
    score_raw = values["score"]

    if not opponents:
        raise ParseError("Поле 'Оппонент:' пусто")

    if len(opponents) == 1:
        # --- Однодуэльный случай: 'Счёт: X:Y в пользу оппонента/игрока' ---
        single_match = SINGLE_SCORE_PATTERN.match(score_raw)
        if not single_match:
            raise ParseError(
                f"Не удалось разобрать счёт: {score_raw!r}. "
                f"Для одного оппонента ожидается формат 'число:число в пользу оппонента/игрока'"
            )
        num1, num2, winner_word = single_match.groups()
        num1, num2 = int(num1), int(num2)
        winner_side = "opponent" if winner_word.lower() in ("оппонента", "тестера") else "player"

        if winner_side == "opponent":
            score_opponent_val, score_player_val = num1, num2
        else:
            score_player_val, score_opponent_val = num1, num2

        duel = Duel(opponent=opponents[0], score_player=score_player_val,
                    score_opponent=score_opponent_val, winner=winner_side)

        return ParsedResult(
            player_name=player_name, kit=kit, region=region,
            tier_before=tier_before, tier_after=tier_after,
            duels=[duel], is_multi_duel=False,
            winner=winner_side,
            score_player=score_player_val, score_opponent=score_opponent_val,
            comment=comment, raw_text=text,
        )

    else:
        # --- Многодуэльный случай (HT1): 'Счёт: X:Y, X:Y, X:Y' (без "в пользу") ---
        score_items = _split_comma_list(score_raw)
        if len(score_items) != len(opponents):
            raise ParseError(
                f"Количество счётов ({len(score_items)}) не совпадает с числом "
                f"оппонентов ({len(opponents)}) - должно быть поровну и в том же порядке"
            )

        duels = []
        for opponent, score_item in zip(opponents, score_items):
            item_match = MULTI_SCORE_ITEM_PATTERN.match(score_item)
            if not item_match:
                raise ParseError(
                    f"Не удалось разобрать счёт {score_item!r} для оппонента {opponent!r}. "
                    f"Ожидается формат 'счётИгрока:счётОппонента', например '4:2'"
                )
            sp, so = int(item_match.group(1)), int(item_match.group(2))
            winner_side = "player" if sp > so else "opponent"
            duels.append(Duel(opponent=opponent, score_player=sp, score_opponent=so, winner=winner_side))

        # Правило HT1: игрок должен выиграть КАЖДЫЙ поединок с разрывом >= 2
        # (например при игре до 4 - счёт оппонента не выше 2). Если хоть
        # один поединок не соответствует - тест целиком считается
        # непройденным (winner='opponent', то есть игрок тест не прошёл).
        all_passed = all(d.winner == "player" and (d.score_player - d.score_opponent) >= 2 for d in duels)
        overall_winner = "player" if all_passed else "opponent"

        agg_score_player = sum(1 for d in duels if d.winner == "player")
        agg_score_opponent = sum(1 for d in duels if d.winner == "opponent")

        return ParsedResult(
            player_name=player_name, kit=kit, region=region,
            tier_before=tier_before, tier_after=tier_after,
            duels=duels, is_multi_duel=True,
            winner=overall_winner,
            score_player=agg_score_player, score_opponent=agg_score_opponent,
            comment=comment, raw_text=text,
        )
