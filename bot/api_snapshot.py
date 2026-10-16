# -*- coding: utf-8 -*-
"""
API для сайта: GET /api/players отдаёт данные игроков из Turso.

Как это устроено (и почему именно так):
  - Соединение с БД живёт ТОЛЬКО в потоке Discord-бота (sqlite3-совместимые
    драйверы не любят общие соединения между потоками). Flask работает в
    другом потоке и к БД НЕ обращается.
  - Поэтому Discord-бот собирает готовый JSON-снимок (SnapshotRefresher.tick),
    кладёт его в память (set_snapshot), а Flask просто отдаёт последний
    снимок (get_snapshot). Запрос к API ничего не читает из базы - он
    мгновенный и не нагружает Turso, сколько бы людей ни открыло сайт.
  - Снимок пересобирается, когда в БД что-то изменилось (бот отметил это
    через mark_dirty после завершённой дуэли) - обычно в пределах пары
    секунд, - и принудительно раз в FORCE_REFRESH_SECONDS на случай, если
    данные поправили в БД напрямую.
  - Если сборка упала, прежний снимок остаётся на месте (сайт продолжает
    показывать последние известные данные), а повтор будет через
    RETRY_SECONDS, а не на каждом шаге цикла.
  - После перезапуска Render память пуста: первый снимок собирается при
    старте Discord-бота из Turso, где данные сохранились.

Модуль намеренно не импортирует ни Flask, ни discord - только стандартную
библиотеку, чтобы его можно было подключать и тестировать где угодно.
"""

import json
import threading
import time
from datetime import datetime, timezone


# Сколько последних дуэлей отдавать у каждого игрока (см. export.build_export_data)
HISTORY_LIMIT = 200
# Принудительная пересборка снимка, даже если никто не отметил изменений
FORCE_REFRESH_SECONDS = 300
# Пауза перед повтором после неудачной сборки
RETRY_SECONDS = 30
# Сколько секунд браузер и прокси могут держать ответ без запроса к серверу
CACHE_MAX_AGE_SECONDS = 5
# Данные публичные (как был публичный players.js), поэтому читать их можно
# с любого сайта - в том числе с GitHub Pages, который живёт на другом домене.
CORS_ORIGIN = "*"


_lock = threading.Lock()
_snapshot = {"body": None, "updated_at": None}


def set_snapshot(players_list, now=None) -> str:
    """Кладёт в память новый снимок. Возвращает время обновления (ISO, UTC)."""
    updated_at = (now or datetime.now(timezone.utc)).isoformat()
    body = json.dumps({"updatedAt": updated_at, "players": players_list}, ensure_ascii=False)
    with _lock:
        _snapshot["body"] = body
        _snapshot["updated_at"] = updated_at
    return updated_at


def get_snapshot():
    """(тело_JSON, время_обновления) или (None, None), если снимка ещё нет."""
    with _lock:
        return _snapshot["body"], _snapshot["updated_at"]


def clear_snapshot() -> None:
    with _lock:
        _snapshot["body"] = None
        _snapshot["updated_at"] = None


class SnapshotRefresher:
    """
    Решает, когда пересобирать снимок. build_fn - функция без аргументов,
    возвращающая список игроков (обычно export.build_export_data).
    Не знает ни про Discord, ни про Flask: tick() вызывается из любого
    периодического цикла, mark_dirty() - когда в БД что-то изменилось.
    """

    def __init__(self, build_fn, clock=time.monotonic,
                 force_refresh_seconds=FORCE_REFRESH_SECONDS, retry_seconds=RETRY_SECONDS):
        self._build = build_fn
        self._clock = clock
        self._force = force_refresh_seconds
        self._retry = retry_seconds
        self._dirty = True            # первый снимок нужен сразу
        self._last_ok = None
        self._not_before = None       # не пытаться раньше этого момента (после сбоя)

    def mark_dirty(self) -> None:
        self._dirty = True

    def tick(self) -> bool:
        """Пересобирает снимок, если пора. True - если собрал новый."""
        now = self._clock()
        if self._not_before is not None and now < self._not_before:
            return False

        due = self._dirty or self._last_ok is None or (now - self._last_ok) >= self._force
        if not due:
            return False

        try:
            players_list = self._build()
        except Exception as e:
            # Прежний снимок остаётся, повторим не сразу - иначе при
            # недоступной БД лог засыпало бы ошибкой каждые несколько секунд.
            print(f"[api] Не удалось собрать снимок данных: {e}")
            self._not_before = now + self._retry
            return False

        set_snapshot(players_list)
        self._dirty = False
        self._last_ok = now
        self._not_before = None
        return True


def build_response():
    """(тело, код, заголовки) для GET /api/players. Не зависит от Flask."""
    body, _updated_at = get_snapshot()
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": CORS_ORIGIN,
    }
    if body is None:
        # Снимка ещё нет (бот только запустился или Discord-часть не
        # настроена) - сайт покажет сообщение и сможет повторить запрос.
        headers["Cache-Control"] = "no-store"
        return json.dumps({"error": "snapshot_not_ready"}), 503, headers

    headers["Cache-Control"] = f"public, max-age={CACHE_MAX_AGE_SECONDS}"
    return body, 200, headers


def register_routes(app) -> None:
    """Подключает GET /api/players к Flask-приложению."""

    @app.route("/api/players")
    def api_players():
        return build_response()
