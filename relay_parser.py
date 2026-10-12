# -*- coding: utf-8 -*-
"""
Разбор сообщений из Discord-ветки #релей (вебхук MultiCraft).

Зафиксированные форматы (из переписки с администратором):

  Старт дуэли - ДВА отдельных сообщения подряд, без кавычек у ников:
      UHC: У игрока {ник} началась дуэль на наборе «{Кит}»
      UHC: С игроком {ник}
  "UHC" - ник администратора, который ставит командные блоки; сам по
  себе текст "UHC:" ничего не значит (админ может писать так и вживую),
  поэтому матчим ТОЛЬКО по полной фразе целиком, не по префиксу.

  Смерть - ОДНО сообщение, ник в кавычках-ёлочках, БЕЗ тега:
      🪦 Игрок «{ник}» <любая причина - падение/бой/лава/вода/...>
  Причина смерти не влияет на исход (кто умер - тот проиграл) и список
  формулировок не полный и будет расти, поэтому матчим по общему
  признаку (🪦 + «ник»), а не по конкретным фразам. Есть "дубликат" без
  кавычек и без эмодзи ("{ник} погиб") - чисто декоративное сообщение
  для чтения в Discord, который НЕ содержит отдельной информации и
  должен игнорироваться, иначе смерть обработается дважды.

  Коннект/дисконнект - с тегом в квадратных скобках, БЕЗ кавычек:
      ↪ [{тег}] {ник} подключился к серверу
      ↩ [{тег}] {ник} отключился от сервера
      ↩ [{тег}] {ник} отключился от сервера (тайм-аут)
  Тег ([RLT2][Tester] и т.п. - средний ранг + роль) для матчмейкинга не
  нужен и не разбирается, нужен только ник. Обычный дисконнект и
  тайм-аут одинаково запускают 3-минутный таймер автопоражения -
  разница есть только в поле timeout (на будущее/для логов).

  Обычный чат формата "[тег] ник: текст" (включая тестовое "relay") -
  НЕ событие, должен игнорироваться. Он отличается от коннекта тем, что
  сразу после ника идёт ":", а не русский глагол.
"""

import re
from dataclasses import dataclass
from typing import Optional, Union


# Ники в примерах: буквы, цифры, подчёркивания, дефисы (включая ведущие/
# конечные, как у "-BaCk-" и "_-XKakTakX-_"). Не включает пробел и ":",
# чтобы не захватить случайно хвост обычного чат-сообщения.
_NICK = r'[A-Za-z0-9_\-]+'

# Один или несколько тег-групп вида [RLT2][Tester] подряд, без пробела
# между собой. Содержимое тега не разбираем - оно боту не нужно.
_TAGS = r'(?:\[[^\]\[]+\])+'

# Эмодзи-стрелки иногда идут с вариативным селектором (↪️/↩️ с U+FE0F),
# иногда без (↪/↩) - нормализуем, вырезая селектор перед матчингом.
_VARIATION_SELECTOR = '\ufe0f'

_RE_DUEL_START_A = re.compile(
    r'^UHC:\s*У игрока\s+(?P<player>' + _NICK + r')\s+'
    r'началась дуэль на наборе\s*«(?P<kit>[^»]+)»\s*$'
)
_RE_DUEL_START_B = re.compile(
    r'^UHC:\s*С игроком\s+(?P<player>' + _NICK + r')\s*$'
)

_RE_DEATH = re.compile(
    r'^\U0001FAA6\s*Игрок\s*«(?P<player>' + _NICK + r')»'
)

_RE_CONNECT = re.compile(
    r'^\u21aa\s*' + _TAGS + r'\s*(?P<player>' + _NICK + r')\s+'
    r'подключился к серверу\s*$'
)
_RE_DISCONNECT = re.compile(
    r'^\u21a9\s*' + _TAGS + r'\s*(?P<player>' + _NICK + r')\s+'
    r'отключился от сервера(?P<timeout>\s*\(тайм-аут\))?\s*$'
)


# ==========================================
# СОБЫТИЯ (на выходе парсера)
# ==========================================

@dataclass(frozen=True)
class DuelStarted:
    kit: str
    player_a: str
    player_b: str


@dataclass(frozen=True)
class PlayerDied:
    player: str


@dataclass(frozen=True)
class PlayerConnected:
    player: str


@dataclass(frozen=True)
class PlayerDisconnected:
    player: str
    timeout: bool


Event = Union[DuelStarted, PlayerDied, PlayerConnected, PlayerDisconnected]


# ==========================================
# РАЗБОР ОДНОГО СООБЩЕНИЯ (без знания о соседних)
# ==========================================

def _normalize(text: str) -> str:
    return text.strip().replace(_VARIATION_SELECTOR, '')


def parse_death(text: str) -> Optional[PlayerDied]:
    m = _RE_DEATH.match(_normalize(text))
    return PlayerDied(player=m.group('player')) if m else None


def parse_connect(text: str) -> Optional[PlayerConnected]:
    m = _RE_CONNECT.match(_normalize(text))
    return PlayerConnected(player=m.group('player')) if m else None


def parse_disconnect(text: str) -> Optional[PlayerDisconnected]:
    m = _RE_DISCONNECT.match(_normalize(text))
    if not m:
        return None
    return PlayerDisconnected(player=m.group('player'), timeout=bool(m.group('timeout')))


def _parse_duel_start_a(text: str):
    """Первая строка старта дуэли ("У игрока ..."). Внутреннее - не
    самостоятельное событие, возвращает (kit, player) либо None."""
    m = _RE_DUEL_START_A.match(_normalize(text))
    return (m.group('kit'), m.group('player')) if m else None


def _parse_duel_start_b(text: str) -> Optional[str]:
    """Вторая строка старта дуэли ("С игроком ..."). Внутреннее - не
    самостоятельное событие, возвращает ник оппонента либо None."""
    m = _RE_DUEL_START_B.match(_normalize(text))
    return m.group('player') if m else None


# ==========================================
# СБОРКА СТАРТА ДУЭЛИ ИЗ ДВУХ СООБЩЕНИЙ
# ==========================================

class RelayParser:
    """
    Разбирает поток сообщений из ветки #релей в события.

    Старт дуэли приходит ДВУМЯ отдельными сообщениями - эта обёртка
    хранит ещё не закрытые "У игрока ..." и соединяет их со следующим
    подходящим "С игроком ...".

    ВАЖНОЕ ДОПУЩЕНИЕ: если две дуэли стартуют почти одновременно (на
    разных китах) и их сообщения чередуются, сопоставление идёт по
    принципу "первый незакрытый -> первая следующая вторая строка"
    (FIFO), а не по какой-то более умной связке - в самих сообщениях
    ничего, кроме текста, не связывает первую и вторую строку одной
    дуэли напрямую (ни id, ни временной метки с точностью для этого).
    Если на практике командный блок гарантированно не чередует две
    пары строк между собой (шлёт их строго одна за другой для одной
    дуэли, прежде чем начать другую), это безопасно. Если окажется,
    что чередование всё же случается - нужен будет другой признак
    связки (например, временной интервал почти 0 между A и B), это
    стоит перепроверить на реальных логах после запуска.
    """

    def __init__(self):
        self._pending = []  # очередь (kit, player_a), ещё не закрытых

    def feed(self, text: str) -> Optional[Event]:
        """Скармливает одно сообщение, возвращает событие либо None
        (сообщение проигнорировано или это первая половина старта
        дуэли, ожидающая вторую)."""
        duel_a = _parse_duel_start_a(text)
        if duel_a is not None:
            self._pending.append(duel_a)
            return None

        duel_b_player = _parse_duel_start_b(text)
        if duel_b_player is not None:
            if not self._pending:
                # "С игроком ..." без предшествующего "У игрока ..." -
                # рассинхрон (например, бот запустился посреди пары
                # сообщений). Игнорируем, восстановиться нечем.
                return None
            kit, player_a = self._pending.pop(0)
            return DuelStarted(kit=kit, player_a=player_a, player_b=duel_b_player)

        event = parse_death(text)
        if event is not None:
            return event

        event = parse_connect(text)
        if event is not None:
            return event

        event = parse_disconnect(text)
        if event is not None:
            return event

        return None  # обычный чат, "relay"-тест и всё остальное - игнорируем
