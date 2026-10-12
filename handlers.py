# -*- coding: utf-8 -*-
"""
Мост между событиями relay_parser.py и слоем db.py.

handle_event(conn, event) - единственная точка входа. Принимает ЛЮБОЕ
событие, которое может вернуть RelayParser.feed(), и решает, что с ним
сделать в БД. Чистая функция от (БД, событие) - не знает про Discord,
легко тестируется скармливанием событий напрямую (как и elo.py/db.py).

Возвращает Outcome - маленький объект с action и подробностями, чтобы
вызывающий код (Discord-бот) мог залогировать/отреагировать эмодзи,
не заглядывая внутрь обработчика.
"""

from dataclasses import dataclass, field
from typing import Optional

import db
from relay_parser import DuelStarted, PlayerConnected, PlayerDied, PlayerDisconnected


@dataclass(frozen=True)
class Outcome:
    action: str
    detail: dict = field(default_factory=dict)


def _ensure_no_active_match(conn, player_id: int, player_name: str) -> Optional[int]:
    """Если у игрока уже есть активный матч (не должно происходить в
    норме - физически он в одном месте), аннулирует его как
    'superseded': это значит, что по нему пропущено завершающее
    событие (скорее всего бот был недоступен). Возвращает id
    аннулированного матча, либо None, если активного матча не было."""
    active = db.find_active_match(conn, player_id)
    if active is None:
        return None
    db.cancel_match(conn, active["id"], reason="superseded")
    return active["id"]


def handle_event(conn, event) -> Outcome:
    if isinstance(event, DuelStarted):
        return _handle_duel_started(conn, event)
    if isinstance(event, PlayerDied):
        return _handle_player_died(conn, event)
    if isinstance(event, PlayerConnected):
        return _handle_player_connected(conn, event)
    if isinstance(event, PlayerDisconnected):
        return _handle_player_disconnected(conn, event)
    raise TypeError(f"неизвестный тип события: {type(event)!r}")


def _handle_duel_started(conn, event: DuelStarted) -> Outcome:
    if event.player_a.lower() == event.player_b.lower():
        # Защитная проверка на уровне домена, а не только на уровне БД
        # (там тоже есть CHECK, но так сообщение понятнее и матч
        # вообще не создаётся частично).
        return Outcome("ignored_same_player", {"player": event.player_a, "kit": event.kit})

    player_a_id = db.get_or_create_player(conn, event.player_a)
    player_b_id = db.get_or_create_player(conn, event.player_b)

    cancelled_a = _ensure_no_active_match(conn, player_a_id, event.player_a)
    cancelled_b = _ensure_no_active_match(conn, player_b_id, event.player_b)

    match_id = db.create_match(conn, kit=event.kit, player_a_name=event.player_a,
                                player_b_name=event.player_b)

    return Outcome("match_started", {
        "match_id": match_id,
        "kit": event.kit,
        "player_a": event.player_a,
        "player_b": event.player_b,
        "cancelled_stale_match_ids": [m for m in (cancelled_a, cancelled_b) if m is not None],
    })


def _handle_player_died(conn, event: PlayerDied) -> Outcome:
    player_id = db.get_or_create_player(conn, event.player)
    match = db.find_active_match(conn, player_id)
    if match is None:
        # Смерть вне какой-либо отслеживаемой дуэли (упал где-то в
        # обычной игре, не в зоне дуэлей) - не наша забота, игнорируем.
        return Outcome("ignored_no_active_match", {"player": event.player, "event": "death"})

    result = db.finish_match(conn, match["id"], loser_player_id=player_id, end_reason="death")
    winner_id = db.get_opponent_id(match, player_id)
    return Outcome("match_finished", {
        "match_id": match["id"],
        "kit": match["kit"],
        "loser": event.player,
        "winner_id": winner_id,
        "winner_delta": result.winner_delta,
        "loser_delta": result.loser_delta,
        "end_reason": "death",
    })


def _handle_player_connected(conn, event: PlayerConnected) -> Outcome:
    player_id = db.get_or_create_player(conn, event.player)
    match = db.find_active_match(conn, player_id)
    if match is None:
        # Коннект вне активной дуэли (обычный вход на сервер) -
        # отменять нечего.
        return Outcome("ignored_no_active_match", {"player": event.player, "event": "connect"})

    db.cancel_disconnect_timer(conn, match["id"], player_id)
    return Outcome("timer_cancelled", {"match_id": match["id"], "player": event.player})


def _handle_player_disconnected(conn, event: PlayerDisconnected) -> Outcome:
    player_id = db.get_or_create_player(conn, event.player)
    match = db.find_active_match(conn, player_id)
    if match is None:
        # Дисконнект вне активной дуэли - нормальный выход с сервера,
        # таймер заводить не на чем.
        return Outcome("ignored_no_active_match", {"player": event.player, "event": "disconnect"})

    db.start_disconnect_timer(conn, match["id"], player_id)
    return Outcome("timer_started", {
        "match_id": match["id"], "player": event.player, "timeout_flag": event.timeout,
    })


def sweep_stale_matches(conn, older_than_minutes: int = 60) -> list:
    """
    Аннулирует активные матчи, которые стартовали давно и, скорее
    всего, "подвисли" из-за недоступности бота (сообщение о смерти/
    дисконнекте пришло, пока бот не слушал канал, и больше не
    повторится). Вызывается ОДИН РАЗ при старте Discord-клиента, не
    по расписанию - в отличие от sweep_expired_timers, которая
    реагирует на штатный, ожидаемый трёхминутный таймер.

    older_than_minutes - намеренно куда больше 3 минут (по умолчанию
    час): обычная дуэль не должна идти часами, и час - это щедрый
    запас, чтобы не аннулировать матч, который на самом деле просто
    ещё идёт.
    """
    outcomes = []
    for row in db.find_stale_active_matches(conn, older_than_minutes):
        db.cancel_match(conn, row["id"], reason="stale_on_restart")
        outcomes.append(Outcome("match_cancelled_stale", {
            "match_id": row["id"], "kit": row["kit"], "started_at": row["started_at"],
        }))
    return outcomes


def sweep_expired_timers(conn) -> list:
    """
    Находит все просроченные (>3 минуты) таймеры дисконнекта и
    засчитывает по ним автопоражение. Вызывается периодически фоновой
    задачей (не из handle_event - это отдельный, не событийный поток).
    Возвращает список Outcome по каждому обработанному таймеру.
    """
    outcomes = []
    for timer_row in db.due_disconnect_timers(conn):
        match = conn.execute(
            "SELECT * FROM matches WHERE id = ?", (timer_row["match_id"],)
        ).fetchone()
        if match is None or match["status"] != "active":
            # Матч уже как-то иначе завершился/аннулировался раньше,
            # чем до него дошла очередь в свипе - таймер неактуален,
            # просто подчищаем и идём дальше.
            db.cancel_disconnect_timer(conn, timer_row["match_id"], timer_row["player_id"])
            continue

        loser_id = timer_row["player_id"]
        result = db.finish_match(conn, match["id"], loser_player_id=loser_id, end_reason="timeout")
        winner_id = db.get_opponent_id(match, loser_id)
        outcomes.append(Outcome("match_finished", {
            "match_id": match["id"],
            "kit": match["kit"],
            "loser_id": loser_id,
            "winner_id": winner_id,
            "winner_delta": result.winner_delta,
            "loser_delta": result.loser_delta,
            "end_reason": "timeout",
        }))
    return outcomes
