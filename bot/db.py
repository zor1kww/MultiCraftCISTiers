
# -*- coding: utf-8 -*-
"""
Слой доступа к БД для эло-системы.

Весь SQL здесь - обычный диалект SQLite, на котором работает и Turso
(libSQL). Два режима подключения:

  - connect(path)          локальный файл/память на стандартном sqlite3
                           (тесты, локальная разработка);
  - connect_turso(url, token)  Turso через пакет `libsql` в режиме
                           embedded replica: локальный файл-копия +
                           синхронизация с облачной базой (чтения
                           локальные, записи уходят в облако).
  - connect_from_env()     выбирает один из двух по переменным окружения
                           TURSO_DATABASE_URL / TURSO_AUTH_TOKEN.

Чтобы код не зависел от особенностей конкретного драйвера (а `libsql`
в этой среде проверить нельзя - нет сети), весь доступ идёт через
тонкую обёртку Connection, которая опирается ТОЛЬКО на то, что есть
у любого sqlite3-совместимого драйвера: execute(sql, params), commit(),
cursor.description, fetchone()/fetchall() с обычными кортежами. Строки
результата собираются в Row (dict) по именам колонок сами, без
row_factory; схема создаётся по одному выражению, без executescript;
id вставленной строки берётся через RETURNING, без lastrowid.

Все функции принимают conn первым аргументом и НЕ коммитят сами
промежуточные шаги - коммит один раз в конце публичной операции
(create_match, finish_match и т.д.), чтобы несколько UPDATE внутри
одной операции были атомарны.

Соединение нельзя делиться между потоками (sqlite3 по умолчанию это
запрещает): каждый поток, который работает с БД, открывает своё.
"""

import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import elo


SCHEMA_PATH = Path(__file__).with_name("schema.sql")
DISCONNECT_TIMEOUT_MINUTES = 3
ANTI_ABUSE_WINDOW_HOURS = elo.ANTI_ABUSE_WINDOW_HOURS


class MatchNotFound(Exception):
    pass


class MatchNotActive(Exception):
    pass


class PlayerNotInMatch(Exception):
    pass


CANCEL_REASONS = ("superseded", "stale_on_restart")


class Row(dict):
    """Строка результата: dict, доступный по имени колонки. Не зависит от
    row_factory драйвера (у libsql его поведение не проверено)."""
    __slots__ = ()


class _Cursor:
    def __init__(self, raw_cursor):
        self._c = raw_cursor

    def _names(self):
        description = self._c.description
        return [col[0] for col in description] if description else []

    def fetchone(self):
        row = self._c.fetchone()
        if row is None:
            return None
        return Row(zip(self._names(), row))

    def fetchall(self):
        names = self._names()
        return [Row(zip(names, row)) for row in self._c.fetchall()]


class Connection:
    """Минимальная обёртка над драйвером (sqlite3 или libsql)."""

    def __init__(self, raw, is_replica: bool = False):
        self._raw = raw
        self.is_replica = is_replica

    def execute(self, sql: str, params=()):
        return _Cursor(self._raw.execute(sql, tuple(params)))

    def commit(self) -> None:
        self._raw.commit()

    def sync(self) -> None:
        """Подтянуть свежее состояние из облака (только embedded replica)."""
        if self.is_replica:
            self._raw.sync()

    def close(self) -> None:
        close = getattr(self._raw, "close", None)
        if close is not None:
            close()


def _raw_connect_local(path: str):
    return sqlite3.connect(path)


def connect(path: str = ":memory:") -> Connection:
    conn = Connection(_raw_connect_local(path))
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def connect_turso(url: str, auth_token: str, local_replica_path: str = "elo_replica.db") -> Connection:
    """Turso через пакет `libsql` (pip install libsql), embedded replica:
    локальный файл + синхронизация с облаком. Локальный файл - только
    кэш: на Render он пропадает при перезапуске, и это нормально, данные
    живут в облачной базе и подтянутся заново."""
    import libsql  # импорт внутри функции: локальные тесты не требуют пакета
    raw = libsql.connect(local_replica_path, sync_url=url, auth_token=auth_token)
    conn = Connection(raw, is_replica=True)
    conn.sync()
    try:
        conn.execute("PRAGMA foreign_keys = ON")
    except Exception as e:  # не критично, если драйвер не принимает PRAGMA
        print(f"[db] PRAGMA foreign_keys не применён: {e}")
    return conn


def connect_from_env() -> Connection:
    """Turso, если заданы TURSO_DATABASE_URL и TURSO_AUTH_TOKEN; иначе
    локальный файл. Если задана только одна из двух переменных - это
    ошибка настройки, а не повод молча уйти на локальный файл."""
    url = os.environ.get("TURSO_DATABASE_URL")
    token = os.environ.get("TURSO_AUTH_TOKEN")
    if bool(url) != bool(token):
        raise RuntimeError(
            "Задана только одна из TURSO_DATABASE_URL / TURSO_AUTH_TOKEN - нужны обе "
            "(или ни одной, для локального файла)."
        )
    if url and token:
        return connect_turso(url, token, os.environ.get("ELO_REPLICA_PATH", "elo_replica.db"))

    path = os.environ.get("ELO_DB_PATH", "elo.db")
    print(f"[db] ВНИМАНИЕ: Turso не настроен, используется ЛОКАЛЬНЫЙ файл {path!r}. "
          f"На Render такой файл пропадает при каждом перезапуске - данные будут потеряны.")
    return connect(path)


def _split_sql_statements(script: str) -> list:
    """Делит SQL-скрипт на отдельные выражения (executescript у драйвера
    может отсутствовать). Убирает комментарии `-- ...` вне строк и
    режет по `;` вне строк."""
    statements, current = [], []
    in_string = False
    i = 0
    while i < len(script):
        ch = script[i]
        if in_string:
            current.append(ch)
            if ch == "'":
                in_string = False
        elif ch == "'":
            in_string = True
            current.append(ch)
        elif ch == "-" and script[i:i + 2] == "--":
            newline = script.find("\n", i)
            i = len(script) if newline == -1 else newline
            continue
        elif ch == ";":
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
        else:
            current.append(ch)
        i += 1
    tail = "".join(current).strip()
    if tail:
        statements.append(tail)
    return statements


# Колонки, добавленные после первого релиза схемы. CREATE TABLE IF NOT
# EXISTS не трогает уже существующую таблицу, поэтому в рабочей базе их
# добавляем ALTER-ом; на свежей базе колонка уже есть и ALTER даёт
# "duplicate column" - это ожидаемо и игнорируется.
_PLAYER_MIGRATIONS = (
    "ALTER TABLE players ADD COLUMN device TEXT",
    "ALTER TABLE players ADD COLUMN removed INTEGER NOT NULL DEFAULT 0",
)


def init_schema(conn: Connection) -> None:
    for statement in _split_sql_statements(SCHEMA_PATH.read_text(encoding="utf-8")):
        conn.execute(statement)
    conn.commit()
    for statement in _PLAYER_MIGRATIONS:
        try:
            conn.execute(statement)
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                raise
    conn.commit()


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ==========================================
# ИГРОКИ И РЕЙТИНГИ
# ==========================================

def get_or_create_player(conn: Connection, name: str, region: Optional[str] = None) -> int:
    row = conn.execute("SELECT id FROM players WHERE name = ? COLLATE NOCASE", (name,)).fetchone()
    if row is not None:
        return row["id"]
    new_row = conn.execute(
        "INSERT INTO players (name, region, created_at) VALUES (?, ?, ?) RETURNING id",
        (name, region, utcnow_iso()),
    ).fetchone()
    conn.commit()
    return new_row["id"]


def set_player_region(conn: Connection, player_id: int, region: str) -> Optional[str]:
    """Ставит игроку регион (перезаписывает прежний). Возвращает прежнее
    значение (None, если региона не было) - для лога."""
    row = conn.execute("SELECT region FROM players WHERE id = ?", (player_id,)).fetchone()
    previous = row["region"] if row is not None else None
    conn.execute("UPDATE players SET region = ? WHERE id = ?", (region, player_id))
    conn.commit()
    return previous


def find_player_id(conn: Connection, name: str) -> Optional[int]:
    """id игрока по нику (без учёта регистра) или None; игрока НЕ создаёт."""
    row = conn.execute("SELECT id FROM players WHERE name = ? COLLATE NOCASE", (name,)).fetchone()
    return row["id"] if row is not None else None


def set_player_device(conn: Connection, player_id: int, device: str) -> Optional[str]:
    """Ставит устройство ('PC' / 'MOBILE'). Возвращает прежнее значение."""
    row = conn.execute("SELECT device FROM players WHERE id = ?", (player_id,)).fetchone()
    previous = row["device"] if row is not None else None
    conn.execute("UPDATE players SET device = ? WHERE id = ?", (device, player_id))
    conn.commit()
    return previous


def set_player_removed(conn: Connection, player_id: int, removed: bool) -> bool:
    """Скрывает игрока из топа (True) или возвращает (False). Возвращает
    прежнее состояние."""
    row = conn.execute("SELECT removed FROM players WHERE id = ?", (player_id,)).fetchone()
    previous = bool(row["removed"]) if row is not None else False
    conn.execute("UPDATE players SET removed = ? WHERE id = ?", (1 if removed else 0, player_id))
    conn.commit()
    return previous


def is_player_excluded(conn: Connection, player_id: int) -> bool:
    """True, если игрок не участвует в рейтинге: отмечен как PC или скрыт
    через remove_player. Дуэли с таким игроком эло не меняют."""
    row = conn.execute("SELECT device, removed FROM players WHERE id = ?", (player_id,)).fetchone()
    if row is None:
        return False
    return row["device"] == "PC" or bool(row["removed"])


def get_elo(conn: Connection, player_id: int, kit: str) -> float:
    """Текущее эло игрока в ките. Если игрок ещё ни разу не играл этот
    кит - НЕ создаёт запись (чистое чтение), просто возвращает
    стартовое значение. Запись в player_ratings появляется только
    когда реально применяется результат матча (upsert_elo)."""
    row = conn.execute(
        "SELECT elo FROM player_ratings WHERE player_id = ? AND kit = ?",
        (player_id, kit),
    ).fetchone()
    return row["elo"] if row is not None else float(elo.STARTING_ELO)


def upsert_elo(conn: Connection, player_id: int, kit: str, new_elo: float) -> None:
    conn.execute(
        """
        INSERT INTO player_ratings (player_id, kit, elo, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT (player_id, kit) DO UPDATE SET elo = excluded.elo, updated_at = excluded.updated_at
        """,
        (player_id, kit, new_elo, utcnow_iso()),
    )


# ==========================================
# АНТИАБУЗ: подсчёт предыдущих дуэлей пары
# ==========================================

def count_prior_duels(conn: Connection, kit: str, player_a_id: int, player_b_id: int,
                       reference_time_iso: str, window_hours: float = ANTI_ABUSE_WINDOW_HOURS) -> int:
    """
    Число ЗАВЕРШЁННЫХ матчей этой пары в этом ките, чьё finished_at
    попадает в окно (reference_time - window_hours, reference_time).

    reference_time_iso - момент, от которого отсчитывается окно назад.
    Берём время СТАРТА текущего матча (а не момента его завершения) -
    так окно не "уезжает" на время самого боя и число не зависит от
    того, сколько шёл конкретный матч.
    """
    low_id, high_id = sorted((player_a_id, player_b_id))
    reference_dt = datetime.fromisoformat(reference_time_iso)
    window_start_iso = (reference_dt - timedelta(hours=window_hours)).isoformat()
    row = conn.execute(
        """
        SELECT COUNT(*) AS n FROM matches
        WHERE kit = ? AND pair_low_id = ? AND pair_high_id = ?
          AND status = 'finished'
          AND finished_at > ? AND finished_at <= ?
        """,
        (kit, low_id, high_id, window_start_iso, reference_time_iso),
    ).fetchone()
    return row["n"]


# ==========================================
# МАТЧИ
# ==========================================

def find_active_match(conn: Connection, player_id: int) -> Optional[Row]:
    """Активный матч игрока, если есть (физически он может быть
    только в одном сразу - используется при старте новой дуэли, чтобы
    не потерять "подвисший" предыдущий матч, и при обработке
    коннект/дисконнект/смерть, чтобы найти, какой матч это касается)."""
    return conn.execute(
        """
        SELECT * FROM matches
        WHERE status = 'active' AND (player_a_id = ? OR player_b_id = ?)
        ORDER BY id DESC LIMIT 1
        """,
        (player_id, player_id),
    ).fetchone()


def get_opponent_id(match_row: Row, player_id: int) -> int:
    if match_row["player_a_id"] == player_id:
        return match_row["player_b_id"]
    if match_row["player_b_id"] == player_id:
        return match_row["player_a_id"]
    raise PlayerNotInMatch(f"игрок {player_id} не участвует в матче {match_row['id']}")


def create_match(conn: Connection, kit: str, player_a_name: str, player_b_name: str) -> int:
    """Создаёт активный матч. Эло обоих фиксируется СЕЙЧАС (на момент
    старта) и больше не пересчитывается до завершения матча."""
    player_a_id = get_or_create_player(conn, player_a_name)
    player_b_id = get_or_create_player(conn, player_b_name)

    started_at = utcnow_iso()
    elo_a = get_elo(conn, player_a_id, kit)
    elo_b = get_elo(conn, player_b_id, kit)
    prior_count = count_prior_duels(conn, kit, player_a_id, player_b_id, started_at)

    low_id, high_id = sorted((player_a_id, player_b_id))
    cur = conn.execute(
        """
        INSERT INTO matches (
            kit, player_a_id, player_b_id, pair_low_id, pair_high_id,
            status, started_at, player_a_elo_before, player_b_elo_before,
            prior_duels_count
        ) VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?, ?)
        RETURNING id
        """,
        (kit, player_a_id, player_b_id, low_id, high_id, started_at, elo_a, elo_b, prior_count),
    )
    new_id = cur.fetchone()["id"]
    conn.commit()
    return new_id


def finish_match(conn: Connection, match_id: int, loser_player_id: int,
                  end_reason: str) -> elo.MatchResult:
    """
    Завершает матч: loser_player_id - тот, кто умер или не вернулся.
    Победитель вычисляется как "второй участник этого же матча" - вызывающему
    коду не нужно отдельно знать, кто победил, достаточно знать, кто
    проиграл (так естественно приходят события - смерть/автопоражение
    всегда называют ПРОИГРАВШЕГО).
    """
    row = conn.execute("SELECT * FROM matches WHERE id = ?", (match_id,)).fetchone()
    if row is None:
        raise MatchNotFound(f"матч {match_id} не найден")
    if row["status"] != "active":
        raise MatchNotActive(f"матч {match_id} уже завершён")

    winner_player_id = get_opponent_id(row, loser_player_id)

    elo_winner_before = (row["player_a_elo_before"] if row["player_a_id"] == winner_player_id
                          else row["player_b_elo_before"])
    elo_loser_before = (row["player_a_elo_before"] if row["player_a_id"] == loser_player_id
                         else row["player_b_elo_before"])

    result = elo.compute_match(
        elo_winner=elo_winner_before,
        elo_loser=elo_loser_before,
        prior_duels_count=row["prior_duels_count"],
    )

    upsert_elo(conn, winner_player_id, row["kit"], result.winner_elo_after)
    upsert_elo(conn, loser_player_id, row["kit"], result.loser_elo_after)

    conn.execute(
        """
        UPDATE matches SET
            status = 'finished', finished_at = ?, winner_id = ?, loser_id = ?,
            end_reason = ?, winner_elo_after = ?, loser_elo_after = ?,
            winner_delta = ?, loser_delta = ?, k_winner = ?, k_loser = ?, m_factor = ?
        WHERE id = ?
        """,
        (
            utcnow_iso(), winner_player_id, loser_player_id, end_reason,
            result.winner_elo_after, result.loser_elo_after,
            result.winner_delta, result.loser_delta,
            result.k_winner, result.k_loser, result.m_factor,
            match_id,
        ),
    )
    conn.execute("DELETE FROM disconnect_timers WHERE match_id = ?", (match_id,))
    conn.commit()
    return result


def cancel_match(conn: Connection, match_id: int, reason: str) -> None:
    """
    Аннулирует активный матч БЕЗ изменения эло ни у кого - штатный
    исход (не ошибка), когда по матчу физически нет и не будет
    завершающего события (например, его подменил новый старт дуэли,
    пока бот был недоступен). cancelled-матчи не попадают в
    player_ratings и не учитываются в антиабуз-окне (там фильтр
    status='finished', cancelled туда не входит).
    """
    if reason not in CANCEL_REASONS:
        raise ValueError(f"неизвестная причина аннулирования: {reason!r}")
    row = conn.execute("SELECT status FROM matches WHERE id = ?", (match_id,)).fetchone()
    if row is None:
        raise MatchNotFound(f"матч {match_id} не найден")
    if row["status"] != "active":
        raise MatchNotActive(f"матч {match_id} уже не активен (status={row['status']})")

    conn.execute(
        "UPDATE matches SET status = 'cancelled', finished_at = ?, end_reason = ? WHERE id = ?",
        (utcnow_iso(), reason, match_id),
    )
    conn.execute("DELETE FROM disconnect_timers WHERE match_id = ?", (match_id,))
    conn.commit()


# ==========================================
# ТАЙМЕРЫ ДИСКОННЕКТА (3 минуты на возврат)
# ==========================================

def start_disconnect_timer(conn: Connection, match_id: int, player_id: int) -> None:
    """Если таймер для этой пары (матч, игрок) уже есть - перезаписывает
    время (на случай повторного дисконнекта без явной отмены - не
    должно происходить в норме, но на всякий случай не плодит дубли)."""
    conn.execute(
        """
        INSERT INTO disconnect_timers (match_id, player_id, disconnected_at)
        VALUES (?, ?, ?)
        ON CONFLICT (match_id, player_id) DO UPDATE SET disconnected_at = excluded.disconnected_at
        """,
        (match_id, player_id, utcnow_iso()),
    )
    conn.commit()


def cancel_disconnect_timer(conn: Connection, match_id: int, player_id: int) -> None:
    conn.execute(
        "DELETE FROM disconnect_timers WHERE match_id = ? AND player_id = ?",
        (match_id, player_id),
    )
    conn.commit()


def find_stale_active_matches(conn: Connection, older_than_minutes: int,
                               now_iso: Optional[str] = None):
    """Активные матчи, которые стартовали давно (старше older_than_minutes)
    и, скорее всего, "подвисли" из-за того, что бот был недоступен и
    пропустил их завершающее событие. Используется один раз при
    старте Discord-клиента - см. handlers.sweep_stale_matches."""
    now_iso = now_iso or utcnow_iso()
    cutoff_iso = (datetime.fromisoformat(now_iso) - timedelta(minutes=older_than_minutes)).isoformat()
    return conn.execute(
        "SELECT * FROM matches WHERE status = 'active' AND started_at <= ?",
        (cutoff_iso,),
    ).fetchall()


def due_disconnect_timers(conn: Connection, now_iso: Optional[str] = None,
                           timeout_minutes: int = DISCONNECT_TIMEOUT_MINUTES):
    """Таймеры, которым пора засчитать автопоражение (просрочили 3
    минуты). Возвращает список строк (match_id, player_id,
    disconnected_at) - обработка (вызов finish_match + удаление
    таймера) остаётся на вызывающей стороне (отдельный цикл/задача по
    расписанию), эта функция только НАХОДИТ просроченные."""
    now_iso = now_iso or utcnow_iso()
    now_dt = datetime.fromisoformat(now_iso)
    cutoff_iso = (now_dt - timedelta(minutes=timeout_minutes)).isoformat()
    return conn.execute(
        "SELECT * FROM disconnect_timers WHERE disconnected_at <= ?",
        (cutoff_iso,),
    ).fetchall()
