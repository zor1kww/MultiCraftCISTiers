# -*- coding: utf-8 -*-
"""
Экспорт эло-системы (Turso) в players.js на GitHub - витрина для
статического сайта, который продолжает читать его как раньше.

Разделено на две части, как и discord_bot.py:
  - build_export_data(conn) - чистая функция, БД -> структура данных.
    Полностью тестируется без сети (test_export.py).
  - publish_to_github(...)  - реальная запись в GitHub через уже
    существующий github_storage.py (переиспользует его конвертер
    JSON<->JS и retry-логику на sha-конфликт). Не тестируется здесь -
    требует сети и токена, как и publish-часть discord_bot.py.

ФОРМАТ ЭКСПОРТА - НОВЫЙ, не такой, как в старой системе тестов:
  - "tiers" у каждого кита теперь несёт ЧИСЛО (elo) и тир, вычисленный
    из него, а не только тир вручную. Поля retired/penaltyByKit из
    старого формата здесь не воспроизводятся - дуэльная система не
    знает этих понятий (ручных тестов и штрафов по дуэльным форматам
    FT2/FT4/FT6 с переходом на эло больше нет - см. подтверждение в
    переписке).
  - "matchHistory" у дуэли нет понятия счёта (4:2 и т.п.) - исход
    смерть/жизнь, а не очки, так что вместо scorePlayer/scoreOpponent
    теперь result: "win"/"loss", eloBefore/eloAfter/delta и endReason
    ("death"/"timeout"), плюс id дуэли и точное время finishedAt.

ВАЖНО, ЧТО ЭТО ЗНАЧИТ ДЛЯ САЙТА: main.js (calcAverageTier,
parseTierInfo, collectGlobalDuels, getTierBadge и т.д.) написан под
СТАРЫЙ формат (scorePlayer/scoreOpponent, retired, penaltyByKit) и
ничего не знает про этот новый. Этот модуль только производит данные -
он НЕ меняет main.js/index.html/css. Пока фронтенд не обновлён под
новый формат, карточки на сайте будут либо падать, либо отображать
пустоту для полей, которых больше нет. Это отдельная, ещё не сделанная
задача (переписать main.js под новый формат matchHistory), а не
недосмотр в этом файле.

РЕГИОН: Discord-релей нигде не передаёт регион игрока (в отличие от
старого ручного шаблона результата, где было явное поле "Регион:") -
поэтому у всех новых игроков region будет null, пока не появится
отдельный способ его указывать (например, через /admin-панель).
"""

import elo
import github_storage


def _format_elo(value: float):
    """Эло всегда должно быть целым (стартует с 1000, меняется только
    на целые дельты) - приводим к int для чистого вывода в players.js,
    но на случай дрейфа не теряем дробную часть, если она вдруг есть."""
    rounded = round(value)
    return rounded if abs(value - rounded) < 1e-9 else value


def build_export_data(conn, skip_players_without_ratings: bool = True) -> list:
    """
    Собирает список игроков из Turso в структуру, готовую к записи в
    players.js (ключи уже такие, какими должны быть в JS-объекте).

    skip_players_without_ratings - по умолчанию True: игрок, который
    есть в таблице players (например, упомянут в "С игроком ...", но
    ни разу не завершил ни одного матча - матч мог быть cancelled),
    не попадает в экспорт, раз показывать по нему нечего (ни одного
    кита с эло). Поставьте False, если нужно видеть и таких игроков
    тоже (с пустыми tiers/matchHistory).
    """
    players_rows = conn.execute(
        "SELECT id, name, region FROM players ORDER BY name COLLATE NOCASE"
    ).fetchall()

    export = []
    for player in players_rows:
        rating_rows = conn.execute(
            "SELECT kit, elo, updated_at FROM player_ratings WHERE player_id = ? ORDER BY kit",
            (player["id"],),
        ).fetchall()

        if not rating_rows and skip_players_without_ratings:
            continue

        tiers = {}
        for rating in rating_rows:
            tiers[rating["kit"]] = {
                "elo": _format_elo(rating["elo"]),
                "tier": elo.get_tier(rating["elo"]),
                "date": rating["updated_at"][:10],  # YYYY-MM-DD
            }

        match_rows = conn.execute(
            """
            SELECT m.*, pa.name AS player_a_name, pb.name AS player_b_name
            FROM matches m
            JOIN players pa ON pa.id = m.player_a_id
            JOIN players pb ON pb.id = m.player_b_id
            WHERE m.status = 'finished' AND (m.player_a_id = ? OR m.player_b_id = ?)
            ORDER BY m.finished_at
            """,
            (player["id"], player["id"]),
        ).fetchall()

        match_history = []
        for m in match_rows:
            is_side_a = m["player_a_id"] == player["id"]
            opponent_name = m["player_b_name"] if is_side_a else m["player_a_name"]
            won = m["winner_id"] == player["id"]
            elo_before = m["player_a_elo_before"] if is_side_a else m["player_b_elo_before"]
            elo_after = m["winner_elo_after"] if won else m["loser_elo_after"]
            delta = m["winner_delta"] if won else -m["loser_delta"]

            match_history.append({
                # id одинаков у обеих сторон одной дуэли - по нему сайт склеивает
                # две записи в одну и не путает дуэли одной пары за один день.
                # finishedAt - точное время (UTC), чтобы порядок внутри дня был верным.
                "id": m["id"],
                "date": (m["finished_at"] or "")[:10],
                "finishedAt": m["finished_at"],
                "kit": m["kit"],
                "opponent": opponent_name,
                "result": "win" if won else "loss",
                "eloBefore": _format_elo(elo_before),
                "eloAfter": _format_elo(elo_after),
                "delta": delta,
                "endReason": m["end_reason"],
            })

        export.append({
            "name": player["name"],
            "region": player["region"],
            "tiers": tiers,
            "matchHistory": match_history,
        })

    return export


def publish_to_github(conn, gh_repo: str, gh_token: str,
                       commit_message: str = "elo: автоматический экспорт из Turso",
                       skip_players_without_ratings: bool = True):
    """
    Собирает данные из Turso и публикует их в players.js на GitHub,
    ПОЛНОСТЬЮ заменяя текущее содержимое массива (не домешивая к нему
    старые записи вручную проведённых тестов). Переиспользует
    update_players_file из github_storage.py - тот же конвертер
    JSON<->JS и retry при sha-конфликте, только mutate_fn здесь
    игнорирует текущее содержимое файла и подставляет свежий снимок
    из БД целиком.
    """
    export_data = build_export_data(conn, skip_players_without_ratings)

    def replace_all(_current_players_list):
        return export_data

    return github_storage.update_players_file(gh_repo, gh_token, replace_all, commit_message)
