# -*- coding: utf-8 -*-
"""
Парсер шаблонного сообщения тестера из закрытой группы.

Шаблон (порядок строк не важен, поля ищутся по меткам):

    Тестер: -999-
    Игрок: Sneger
    Кит: Gapple
    Регион: RU
    Предыдущий ранг: LT3
    Полученный ранг: LT1
    Счёт: 2:0 в пользу тестера
    Комментарий: (необязательно)

Обязательные поля: Тестер, Игрок, Кит, Регион, Предыдущий ранг,
Полученный ранг, Счёт. Если хотя бы одно из них не найдено - сообщение
считается НЕ результатом (обычное обсуждение в топике) и игнорируется
без ошибки.

Соперник в дуэли всегда - сам тестер (поле "Тестер:"), отдельного поля
для соперника нет по договорённости.
"""

import re
from dataclasses import dataclass
from typing import Optional

from bot_config import VALID_KITS, REGIONS, TIER_ORDER


REQUIRED_FIELD_LABELS = {
    "tester": ["тестер"],
    "player": ["игрок"],
    "kit": ["кит"],
    "region": ["регион"],
    "tier_before": ["предыдущий ранг"],
    "tier_after": ["полученный ранг"],
    "score": ["счёт", "счет"],  # поддерживаем написание и с ё, и без
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

SCORE_PATTERN = re.compile(
    r"(\d{1,2})\s*[:\-]\s*(\d{1,2})\s+в\s+пользу\s+(тестера|игрока)",
    re.IGNORECASE
)


@dataclass
class ParsedResult:
    tester_name: str
    player_name: str
    kit: str
    region: str
    tier_before: str
    tier_after: str
    score_tester: int
    score_player: int
    winner: str          # "tester" или "player"
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
        # метка в начале строки, затем двоеточие, затем значение до конца строки
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


def parse_result_message(text: str) -> Optional[ParsedResult]:
    """
    Пытается распарсить текст сообщения как результат теста.

    Возвращает ParsedResult при успехе.
    Возвращает None, если сообщение явно не похоже на результат
    (меньше 2 меток найдено вообще) - значит это обычное обсуждение,
    молча игнорируем.
    Бросает ParseError, если сообщение ПОХОЖЕ на результат (2+ метки),
    но не хватает обязательных полей или значения некорректны - в этом
    случае стоит ответить тестеру с описанием проблемы.
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

    # --- Валидация и нормализация значений ---

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

    score_raw = values["score"]
    score_match = SCORE_PATTERN.search(score_raw)
    if not score_match:
        raise ParseError(
            f"Не удалось разобрать счёт: {score_raw!r}. "
            f"Ожидается формат 'число:число в пользу тестера/игрока'"
        )
    num1, num2, winner_word = score_match.groups()
    num1, num2 = int(num1), int(num2)
    winner = "tester" if winner_word.lower() == "тестера" else "player"

    # По договорённости первое число в счёте относится к тому, "в чью пользу"
    # написано - т.е. "2:0 в пользу тестера" значит у тестера 2, у игрока 0.
    if winner == "tester":
        score_tester, score_player = num1, num2
    else:
        score_tester, score_player = num2, num1

    comment = _extract_field(text, OPTIONAL_FIELD_LABELS["comment"]) or None

    return ParsedResult(
        tester_name=values["tester"],
        player_name=values["player"],
        kit=kit,
        region=region,
        tier_before=tier_before,
        tier_after=tier_after,
        score_tester=score_tester,
        score_player=score_player,
        winner=winner,
        comment=comment,
        raw_text=text,
    )
