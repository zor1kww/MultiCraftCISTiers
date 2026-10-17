# -*- coding: utf-8 -*-
"""
Связка "текст одного сообщения -> событие -> действие в БД", без какой
бы то ни было зависимости от discord.py. Вынесена отдельно от
discord_bot.py нарочно: этот файл можно тестировать без установленной
библиотеки discord.py и без реального подключения к Discord, а
discord_bot.py остаётся тонкой обвязкой поверх него (подписка на канал,
старт фоновых задач) - сам по себе почти без логики, которую имело бы
смысл тестировать отдельно от реального Discord-соединения.
"""

from typing import Optional

import handlers
from relay_parser import RelayParser


def process_message(conn, parser: RelayParser, text: str) -> Optional[handlers.Outcome]:
    """Одно сообщение из ветки #релей -> либо Outcome (что-то реально
    произошло в БД), либо None (сообщение ни на что не похоже, или это
    первая половина старта дуэли - ждём вторую)."""
    event = parser.feed(text)
    if event is None:
        return None
    return handlers.handle_event(conn, event)


def extract_texts(content, embeds=()):
    """
    Тексты одного Discord-сообщения, которые нужно отдать парсеру.

    Часть событий релея приходит не обычным текстом, а EMBED-блоком
    (на скриншоте канала это строки с цветной полоской слева: коннект/
    дисконнект и "ник погиб"), и у такого сообщения message.content
    ПУСТОЙ - текст лежит в embed.description (или embed.title).
    Поэтому берём content и текст каждого embed, режем многострочные
    тексты на отдельные строки, без пустых строк и дублей (одно и то же событие не должно обработаться дважды, если
    текст продублирован в title и description).

    embeds - любой набор объектов с атрибутами title/description
    (настоящие discord.Embed или заглушки в тестах).
    """
    texts = []

    def add(value):
        # Релей может прислать несколько событий ОДНИМ сообщением, по
        # строке на событие (например, обе строки старта дуэли). Парсер
        # рассчитан на одну строку = одно событие, поэтому режем здесь.
        if isinstance(value, str):
            for line in value.splitlines():
                line = line.strip()
                if line and line not in texts:
                    texts.append(line)

    add(content)
    for embed in embeds or ():
        add(getattr(embed, "description", None))
        add(getattr(embed, "title", None))
    return texts
