# -*- coding: utf-8 -*-
"""
Discord-клиент эло-системы: слушает канал #релей, превращает сообщения
в события (relay_parser.py) и действия в БД (handlers.py) через
relay_bot_core.process_message.

ВАЖНО: этот файл, в отличие от elo.py/relay_parser.py/db.py/handlers.py/
relay_bot_core.py, НЕ покрыт тестами в этом чате - здесь нет сети и
нет библиотеки discord.py, чтобы по-настоящему подключиться и
проверить. Вся логика, которую можно было протестировать без реального
Discord-соединения, вынесена в relay_bot_core.py и проверена там. Этот
файл - тонкая, насколько получилось, обвязка поверх неё: подписка на
канал и два фоновых цикла. Проверить его можно только вживую, с
реальным токеном бота и реальным каналом.

Переменные окружения (по аналогии с TG_TOKEN/GH_TOKEN в main.py):
    DISCORD_BOT_TOKEN        - токен Discord-бота (developer portal)
    DISCORD_RELAY_CHANNEL_ID - id канала #релей (число)
    TURSO_DATABASE_URL       - URL базы Turso (libsql://...)
    TURSO_AUTH_TOKEN         - токен доступа к ней
    ELO_REPLICA_PATH         - (необязательно) путь локального файла-реплики
    ELO_DB_PATH              - только для локального запуска БЕЗ Turso
                               (см. db.connect_from_env)

Требуются библиотеки discord.py и libsql (`pip install discord.py libsql`) -
в этой среде их нет, поэтому настоящее подключение здесь не проверялось.
"""

import os

import discord
from discord.ext import tasks

import db
import handlers
from relay_bot_core import extract_texts, process_message
from relay_parser import RelayParser


DISCORD_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
RELAY_CHANNEL_ID_RAW = os.environ.get("DISCORD_RELAY_CHANNEL_ID")

# Раз в сколько секунд проверяем просроченные (>3 мин) таймеры дисконнекта.
TIMER_SWEEP_INTERVAL_SECONDS = 20
# Порог "подвисшего" активного матча при старте бота - см. handlers.sweep_stale_matches.
STALE_MATCH_THRESHOLD_MINUTES = 60

intents = discord.Intents.default()
intents.message_content = True  # без этого on_message не увидит текст сообщения


class RelayClient(discord.Client):
    def __init__(self, conn, relay_channel_id: int, **kwargs):
        super().__init__(intents=intents, **kwargs)
        self.conn = conn
        self.relay_channel_id = relay_channel_id
        self.parser = RelayParser()

    async def on_ready(self):
        print(f"[discord] Бот запущен как {self.user}, слушаю канал {self.relay_channel_id}")

        # Разовая зачистка подвисших с прошлого запуска матчей - см.
        # docstring handlers.sweep_stale_matches про то, зачем это нужно.
        stale_outcomes = handlers.sweep_stale_matches(self.conn, STALE_MATCH_THRESHOLD_MINUTES)
        for outcome in stale_outcomes:
            print(f"[discord] При старте аннулирован подвисший матч: {outcome.detail}")

        # on_ready может сработать повторно при переподключении -
        # не запускаем вторую копию цикла поверх уже идущей.
        if not timer_sweep_loop.is_running():
            timer_sweep_loop.start(self)

    async def on_message(self, message: discord.Message):
        if message.channel.id != self.relay_channel_id:
            return

        # Свои сообщения НАМЕРЕННО не фильтруем: наш бот в этот канал
        # ничего не пишет, а встроенный релей MultiCraft может публиковать
        # события от имени того же бота-приложения, под токеном которого
        # мы слушаем канал, - фильтр по автору отбросил бы все события.

        # Часть событий (коннект/дисконнект) приходит embed-блоком с
        # пустым content - берём текст и оттуда (см. extract_texts).
        for text in extract_texts(message.content, message.embeds):
            try:
                outcome = process_message(self.conn, self.parser, text)
            except Exception as e:
                # Один кривой/неожиданный текст не должен ронять весь
                # процесс - логируем и едем дальше, как и в остальном боте.
                print(f"[discord] Ошибка обработки сообщения {message.id!r}: {e}")
                continue

            if outcome is not None:
                print(f"[discord] {outcome.action}: {outcome.detail}")


@tasks.loop(seconds=TIMER_SWEEP_INTERVAL_SECONDS)
async def timer_sweep_loop(client: RelayClient):
    try:
        outcomes = handlers.sweep_expired_timers(client.conn)
    except Exception as e:
        print(f"[discord] Ошибка свипа таймеров: {e}")
        return
    for outcome in outcomes:
        print(f"[discord] Автопоражение по таймеру: {outcome.detail}")


def run():
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_BOT_TOKEN не задан")
    if not RELAY_CHANNEL_ID_RAW:
        raise RuntimeError("DISCORD_RELAY_CHANNEL_ID не задан")
    relay_channel_id = int(RELAY_CHANNEL_ID_RAW)

    # Соединение открывается здесь, В ПОТОКЕ Discord-бота, и используется
    # только в нём (событийный цикл discord.py и tasks.loop - один поток):
    # sqlite3-совместимые драйверы не любят общие соединения между потоками.
    conn = db.connect_from_env()
    db.init_schema(conn)  # CREATE ... IF NOT EXISTS - безопасно повторять

    client = RelayClient(conn, relay_channel_id)
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    run()
