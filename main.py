# -*- coding: utf-8 -*-
"""
MultiCraftCISTiers - точка входа сервиса (Render).

Что запускается:
  - Flask: GET / (health-check), GET /api/players (Elo, мини-игры), GET /api/pts (киты);
  - Discord-бот (поток): слушает #релей, команды через \\ (\\set_region, \\set_device,
    \\remove_player, \\restore_player, \\tiertest), тиртесты, снимки для сайта,
    итоговые посты в Telegram (через bot/telegram_results.py, requests, без polling);
  - необязательно: Telegram-админка Elo (bot/elo_admin_panel.py), если есть TG_TOKEN.

Данные PTS живут только в Turso. players.js и GitHub API больше не используются,
старый Telegram-бот (telegram_legacy/) не запускается.
"""

import os
import sys
import time
import traceback
from pathlib import Path
from threading import Thread

_ROOT = Path(__file__).parent
_BOT_DIR = str(_ROOT / "bot")
if _BOT_DIR not in sys.path:
    sys.path.insert(0, _BOT_DIR)
# Запасной путь: elo_admin_* могут импортировать модули из telegram_legacy/.
# Ставим В КОНЕЦ, чтобы файлы из bot/ имели приоритет. Сам старый бот не запускается.
_LEGACY_DIR = str(_ROOT / "telegram_legacy")
if _LEGACY_DIR not in sys.path:
    sys.path.append(_LEGACY_DIR)

from flask import Flask

import api_snapshot

# Discord-слой импортируется защищённо: сбой импорта не должен ронять health-check.
try:
    import discord_bot
    _DISCORD_IMPORT_ERROR = None
except Exception as e:  # noqa: BLE001
    discord_bot = None
    _DISCORD_IMPORT_ERROR = e
    traceback.print_exc()

app = Flask(__name__)
api_snapshot.register_routes(app)  # /api/players и /api/pts


@app.route("/")
def home():
    return "I am alive!"


def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


def start_discord():
    if discord_bot is None:
        print(f"Discord-бот не запущен: модуль не импортировался ({_DISCORD_IMPORT_ERROR!r}). "
              f"Проверьте requirements.txt (discord.py, libsql) и наличие файлов в bot/.")
        return None
    if not (os.environ.get("DISCORD_BOT_TOKEN") and os.environ.get("DISCORD_RELAY_CHANNEL_ID")):
        print("DISCORD_BOT_TOKEN/DISCORD_RELAY_CHANNEL_ID не заданы - Discord-бот не запущен.")
        return None
    print("Запуск Discord-бота...")
    t = Thread(target=discord_bot.run, daemon=True)
    t.start()
    return t


def start_telegram_admin():
    """Админка Elo в Telegram (необязательна). Возвращает telebot или None."""
    token = os.environ.get("TG_TOKEN")
    if not token:
        return None
    try:
        import telebot
        import elo_admin_panel
        bot = telebot.TeleBot(token)
        elo_admin_panel.register(bot)
        return bot
    except Exception as e:  # noqa: BLE001
        print(f"Админ-панель эло не подключена: {e}")
        return None


if __name__ == "__main__":
    print("Запуск веб-сервера...")
    Thread(target=run_web_server, daemon=True).start()

    discord_thread = start_discord()
    tg_bot = start_telegram_admin()

    if tg_bot is not None:
        print("Telegram: админка подключена, слушаю...")
        tg_bot.infinity_polling()  # блокирует основной поток
    else:
        print("Сервис запущен.")
        while True:  # держим процесс живым (Flask и Discord - в потоках)
            time.sleep(3600)
