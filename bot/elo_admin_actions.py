"""
Действия админ-панели над базой эло. Все функции принимают conn и
выполняются в потоке Discord (через db_executor), Telegram здесь не
участвует - поэтому их можно тестировать отдельно от панели.

Ручные правки НЕ создают записей в matches: они пишутся в admin_log.
"""

from datetime import datetime, timezone
from typing import Optional

import db
import elo
from handlers import ALLOWED_REGIONS

# Киты, по которым панель предлагает править эло (как maintiers + subtiers
# в js/config.js).
KITS = (
    "Hardcore", "Manhunt", "Diamond Pot", "Beast", "Emerald", "Emerald Pot",
    "RVM", "Dragonhide", "Pickaxe", "SMP", "Vanilla",
    "Combo", "Gapple", "Mace", "Crystal",
)

MAX_ELO = 5000
START_ELO = 1000


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ==========================================
# ЖУРНАЛ И НАСТРОЙКИ
# ==========================================

def log_action(conn, admin: str, action: str, details: str) -> None:
    conn.execute(
        "INSERT INTO admin_log (ts, admin_id, action, details) VALUES (?, ?, ?, ?)",
        (_now(), str(admin), action, details),
    )
    conn.commit()


def recent_log(conn, limit: int = 10) -> list:
    rows = conn.execute(
        "SELECT ts, admin_id, action, details FROM admin_log ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    return [dict(ts=r["ts"], admin=r["admin_id"], action=r["action"], details=r["details"]) for r in rows]


def get_setting(conn, key: str, default: Optional[str] = None) -> Optional[str]:
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row is not None else default


def set_setting(conn, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT (key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    conn.commit()


def _publisher():
    try:
        import telegram_results
        return telegram_results.get_publisher()
    except Exception:  # публикация необязательна
        return None


def apply_settings(conn) -> None:
    """Применяет сохранённые настройки к работающему боту. Вызывается при
    старте и после каждого изменения из панели."""
    win_bonus = get_setting(conn, "win_bonus")
    if win_bonus in ("1", "2"):
        elo.WIN_BONUS_MULTIPLIER = int(win_bonus)
    tg_results = get_setting(conn, "tg_results")
    if tg_results is not None:
        pub = _publisher()
        if pub is not None:
            pub.set_enabled(tg_results == "1")


def settings_state(conn) -> dict:
    pub = _publisher()
    return {
        "win_bonus": elo.WIN_BONUS_MULTIPLIER,
        "tg_enabled": bool(pub and pub.enabled),
        "tg_possible": bool(pub and pub.can_send),
    }


def set_win_bonus(conn, admin: str, value: int) -> None:
    if value not in (1, 2):
        raise ValueError("множитель победы: 1 или 2")
    set_setting(conn, "win_bonus", str(value))
    apply_settings(conn)
    log_action(conn, admin, "win_bonus", f"множитель победы = ×{value}")


def set_tg_results(conn, admin: str, enabled: bool) -> None:
    set_setting(conn, "tg_results", "1" if enabled else "0")
    apply_settings(conn)
    log_action(conn, admin, "tg_results", "публикация результатов " + ("включена" if enabled else "выключена"))


# ==========================================
# ИГРОКИ
# ==========================================

def resolve_player(conn, query: str) -> Optional[int]:
    """id игрока по нику (без учёта регистра) или None."""
    return db.find_player_id(conn, query.strip())


def recent_matches(conn, limit: int = 10, player_id: Optional[int] = None) -> list:
    sql = (
        "SELECT m.id, m.kit, m.finished_at, m.end_reason, m.winner_delta, m.loser_delta, "
        "       w.name AS winner, l.name AS loser "
        "FROM matches m "
        "JOIN players w ON w.id = m.winner_id "
        "JOIN players l ON l.id = m.loser_id "
        "WHERE m.status = 'finished' "
    )
    params = []
    if player_id is not None:
        sql += "AND (m.player_a_id = ? OR m.player_b_id = ?) "
        params += [player_id, player_id]
    sql += "ORDER BY m.finished_at DESC, m.id DESC LIMIT ?"
    params.append(limit)
    return [dict(r) for r in conn.execute(sql, tuple(params)).fetchall()]


def player_card(conn, player_id: int) -> Optional[dict]:
    p = conn.execute(
        "SELECT id, name, region, device, removed FROM players WHERE id = ?", (player_id,)
    ).fetchone()
    if p is None:
        return None
    ratings = [
        {"kit": r["kit"], "elo": r["elo"], "tier": elo.get_tier(r["elo"])}
        for r in conn.execute(
            "SELECT kit, elo FROM player_ratings WHERE player_id = ? ORDER BY elo DESC", (player_id,)
        ).fetchall()
    ]
    return {
        "id": p["id"], "name": p["name"], "region": p["region"], "device": p["device"],
        "removed": bool(p["removed"]), "ratings": ratings,
        "matches": recent_matches(conn, limit=5, player_id=player_id),
    }


def _name(conn, player_id: int) -> str:
    row = conn.execute("SELECT name FROM players WHERE id = ?", (player_id,)).fetchone()
    return row["name"] if row is not None else f"#{player_id}"


def set_player_elo(conn, admin: str, player_id: int, kit: str, value: float) -> tuple:
    """Ставит эло вручную. Возвращает (было, стало)."""
    if not (0 <= value <= MAX_ELO):
        raise ValueError(f"эло должно быть от 0 до {MAX_ELO}")
    previous = db.get_elo(conn, player_id, kit)
    db.upsert_elo(conn, player_id, kit, float(value))
    conn.commit()
    log_action(conn, admin, "set_elo", f"{_name(conn, player_id)} / {kit}: {previous:g} -> {value:g}")
    return previous, float(value)


def reset_player_elo(conn, admin: str, player_id: int, kit: str) -> tuple:
    """Сбрасывает эло на ките до стартовых 1000 (HT5)."""
    previous = db.get_elo(conn, player_id, kit)
    db.upsert_elo(conn, player_id, kit, float(START_ELO))
    conn.commit()
    log_action(conn, admin, "reset_elo", f"{_name(conn, player_id)} / {kit}: {previous:g} -> {START_ELO}")
    return previous, float(START_ELO)


def set_region(conn, admin: str, player_id: int, region: Optional[str]) -> Optional[str]:
    if region is not None and region not in ALLOWED_REGIONS:
        raise ValueError("неизвестный регион")
    previous = db.set_player_region(conn, player_id, region)
    log_action(conn, admin, "set_region", f"{_name(conn, player_id)}: {previous} -> {region}")
    return previous


def set_device(conn, admin: str, player_id: int, device: str) -> Optional[str]:
    if device not in ("PC", "MOBILE"):
        raise ValueError("устройство: PC или MOBILE")
    previous = db.set_player_device(conn, player_id, device)
    log_action(conn, admin, "set_device", f"{_name(conn, player_id)}: {previous} -> {device}")
    return previous


def set_removed(conn, admin: str, player_id: int, removed: bool) -> bool:
    previous = db.set_player_removed(conn, player_id, removed)
    log_action(conn, admin, "remove_player" if removed else "restore_player", _name(conn, player_id))
    return previous


# ==========================================
# АННУЛИРОВАНИЕ ДУЭЛИ
# ==========================================

def match_details(conn, match_id: int) -> Optional[dict]:
    m = conn.execute(
        """
        SELECT m.*, pa.name AS a_name, pb.name AS b_name
        FROM matches m
        JOIN players pa ON pa.id = m.player_a_id
        JOIN players pb ON pb.id = m.player_b_id
        WHERE m.id = ?
        """,
        (match_id,),
    ).fetchone()
    if m is None:
        return None
    d = dict(m)
    if d["winner_id"] is not None:
        winner_is_a = d["winner_id"] == d["player_a_id"]
        d["winner"] = d["a_name"] if winner_is_a else d["b_name"]
        d["loser"] = d["b_name"] if winner_is_a else d["a_name"]
        d["winner_before"] = d["player_a_elo_before"] if winner_is_a else d["player_b_elo_before"]
        d["loser_before"] = d["player_b_elo_before"] if winner_is_a else d["player_a_elo_before"]
    return d


def void_match(conn, admin: str, match_id: int) -> str:
    """
    Аннулирует завершённую дуэль: возвращает обоим игрокам эло до матча
    и помечает матч как cancelled (он пропадает из истории и из
    антиабуз-окна). Откат делается ТОЛЬКО если с тех пор эло обоих на
    этом ките не менялось (нет более поздних дуэлей и ручных правок):
    иначе простое возвращение старых чисел затёрло бы чужие изменения.
    Бросает ValueError с понятным текстом, если откат невозможен.
    """
    d = match_details(conn, match_id)
    if d is None:
        raise ValueError("дуэль не найдена")
    if d["status"] != "finished":
        raise ValueError("аннулировать можно только завершённую дуэль")

    winner_id, loser_id, kit = d["winner_id"], d["loser_id"], d["kit"]
    now_winner = db.get_elo(conn, winner_id, kit)
    now_loser = db.get_elo(conn, loser_id, kit)
    if abs(now_winner - d["winner_elo_after"]) > 1e-6 or abs(now_loser - d["loser_elo_after"]) > 1e-6:
        raise ValueError(
            "после этой дуэли эло игроков на этом ките уже менялось (другие дуэли или "
            "ручная правка) - автоматический откат невозможен, поправьте эло вручную"
        )

    db.upsert_elo(conn, winner_id, kit, d["winner_before"])
    db.upsert_elo(conn, loser_id, kit, d["loser_before"])
    conn.execute("UPDATE matches SET status = 'cancelled' WHERE id = ?", (match_id,))
    conn.commit()
    msg = (f"дуэль #{match_id} ({kit}) аннулирована: {d['winner']} {now_winner:g} -> {d['winner_before']:g}, "
           f"{d['loser']} {now_loser:g} -> {d['loser_before']:g}")
    log_action(conn, admin, "void_match", msg)
    return msg
