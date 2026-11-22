# -*- coding: utf-8 -*-
"""
Разовый импорт старых EU-игроков (убранных из players.js) в Turso.

Правила импорта:
  - регион всем: EU; устройство PH/TB -> MOBILE (PC в топ не попадает, здесь PC нет);
  - потолок ранга LT2: любой ранг выше LT2 (HT1, LT1, HT2) понижается до HT3;
  - Retired ставится на киты с рангом 1-3 (HT/LT/MT 1-3; по правилу сайта выше нельзя);
    киты с рангом 4-5 остаются без Retired (в отчёте они помечены);
  - штрафов и истории нет; существующих в базе игроков/киты не перезаписывает.

Запуск: переменная окружения PTS_IMPORT_OLD_EU=report (только отчёт) или apply (запись).
Повторная запись блокируется отметкой pts_old_eu_imported_at в settings.
После apply переменную убрать.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import db

DATA_FILE = Path(__file__).with_name("old_eu_players.json")
MARKER = "pts_old_eu_imported_at"
DEFAULT_DATE = "2026-01-01"
REGION = "EU"
CAP_FROM = {"HT1", "LT1", "HT2"}   # выше LT2
CAP_TO = "HT3"
RETIRE_ALLOWED = {"HT1", "MT1", "LT1", "HT2", "MT2", "LT2", "HT3", "MT3", "LT3"}
DEVICE_MAP = {"PH": "MOBILE", "TB": "MOBILE", "PC": "PC", "MOBILE": "MOBILE"}


def _prepare(entry: dict) -> dict:
    ratings, capped, cannot_retire = [], [], []
    for kit, data in entry["tiers"].items():
        tier = data["tier"]
        if tier in CAP_FROM:
            capped.append(f"{kit}: {tier}->{CAP_TO}")
            tier = CAP_TO
        retired = 1 if tier in RETIRE_ALLOWED else 0
        if not retired:
            cannot_retire.append(f"{kit} {tier}" + (" (в источнике был R)" if data.get("was_retired") else ""))
        ratings.append({"kit": kit, "tier": tier, "retired": retired})
    return {
        "name": entry["name"],
        "device": DEVICE_MAP.get(str(entry.get("device") or "").upper()),
        "ratings": ratings,
        "capped": capped,
        "cannot_retire": cannot_retire,
    }


def build_plan() -> list:
    entries = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return [_prepare(e) for e in entries]


def format_report(plan: list) -> str:
    lines = [f"Старые EU: игроков {len(plan)}, рангов {sum(len(p['ratings']) for p in plan)}"]
    for p in plan:
        if p["capped"]:
            lines.append(f"  потолок LT2: {p['name']}: {', '.join(p['capped'])}")
    no_ret = [p["name"] for p in plan if all(not r["retired"] for r in p["ratings"])]
    if no_ret:
        lines.append(f"  без Retired вообще (все киты ниже ранга 3): {', '.join(no_ret)}")
    partial = [f"{p['name']} ({', '.join(p['cannot_retire'])})" for p in plan
               if p["cannot_retire"] and any(r["retired"] for r in p["ratings"])]
    if partial:
        lines.append(f"  Retired только на части китов: {'; '.join(partial)}")
    return "\n".join(lines)


def already_imported(conn) -> bool:
    return conn.execute("SELECT 1 FROM settings WHERE key = ?", (MARKER,)).fetchone() is not None


def apply_plan(conn, plan: list) -> dict:
    if already_imported(conn):
        raise RuntimeError("Импорт старых EU уже выполнен (отметка в settings).")
    written = {"players_created": 0, "players_existing_skipped_region": 0, "ratings": 0, "ratings_skipped": 0}
    for p in plan:
        existing = db.find_player_id(conn, p["name"])
        player_id = existing if existing is not None else db.get_or_create_player(conn, p["name"])
        if existing is None:
            written["players_created"] += 1
            db.set_player_region(conn, player_id, REGION)
            if p["device"]:
                db.set_player_device(conn, player_id, p["device"])
        else:
            written["players_existing_skipped_region"] += 1   # регион/устройство существующего не трогаем
        for r in p["ratings"]:
            cur = conn.execute(
                "INSERT INTO pts_ratings (player_id, kit, tier, set_date, retired) VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT (player_id, kit) DO NOTHING",
                (player_id, r["kit"], r["tier"], DEFAULT_DATE, r["retired"]),
            )
            if getattr(cur, "rowcount", 1) == 0:
                written["ratings_skipped"] += 1
            else:
                written["ratings"] += 1
        conn.commit()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT (key) DO UPDATE SET value = excluded.value",
        (MARKER, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    return written


def run_from_env(conn) -> None:
    mode = os.environ.get("PTS_IMPORT_OLD_EU", "").strip().lower()
    if mode not in ("report", "apply"):
        return
    try:
        plan = build_plan()
        print("[old-eu] ОТЧЁТ\n" + format_report(plan))
        if mode == "apply":
            print("[old-eu] ЗАПИСЬ:", apply_plan(conn, plan))
    except Exception as e:  # noqa: BLE001
        print(f"[old-eu] ошибка: {e}")
