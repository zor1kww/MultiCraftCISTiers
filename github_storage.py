# -*- coding: utf-8 -*-
"""
Чтение/запись players/players.js в GitHub через Contents API.

Конвертация JS<->JSON - та же техника, что была в исходном main.py
(голые ключи объекта оборачиваются в кавычки регуляркой и обратно).
Проверена в migrate_players.py на реальных данных - оставляю тот же
подход для консистентности, а не переизобретаю парсинг.

Отличие от исходной версии: добавлен retry при конфликте sha
(409/422 - файл изменился между чтением и записью, например если
тестер А и тестер Б отправляют результаты почти одновременно).
"""

import re
import json
import base64
import time
import requests

FILE_PATH = "players/players.js"
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1.5


class GithubStorageError(Exception):
    pass


def _js_to_json_text(raw_js: str) -> str:
    return re.sub(r'(?<=[{,\s])(\w+)(\s*):', r'"\1"\2:', raw_js)


def _json_to_js_text(json_text: str) -> str:
    return re.sub(r'"(\w+)"\s*:', r'\1:', json_text)


def _get_file(gh_repo: str, gh_token: str):
    """Возвращает (players_list, sha, raw_content, prefix, suffix)."""
    url = f"https://api.github.com/repos/{gh_repo}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {gh_token}"}

    response = requests.get(url, headers=headers, timeout=15)
    if response.status_code != 200:
        raise GithubStorageError(f"Ошибка GitHub при чтении файла: {response.status_code}")

    file_data = response.json()
    sha = file_data['sha']
    content = base64.b64decode(file_data['content']).decode('utf-8')

    match = re.search(r"=\s*(\[.*\]);?\s*$", content, re.DOTALL)
    if not match:
        match = re.search(r"(\[.*\])", content, re.DOTALL)
        if not match:
            raise GithubStorageError("Не удалось найти структуру массива в players.js")

    raw_array_text = match.group(1)
    json_text = _js_to_json_text(raw_array_text)

    try:
        players_list = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise GithubStorageError(f"Ошибка парсинга JSON: {e}")

    prefix = content.split('[')[0]
    suffix = ";" if content.strip().endswith(';') else ""

    return players_list, sha, prefix, suffix


def _put_file(gh_repo: str, gh_token: str, players_list, sha: str, prefix: str, suffix: str, commit_message: str):
    url = f"https://api.github.com/repos/{gh_repo}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {gh_token}"}

    new_json_text = json.dumps(players_list, indent=4, ensure_ascii=False)
    new_js_text = _json_to_js_text(new_json_text)
    new_file_content = f"{prefix}{new_js_text}{suffix}\n"
    new_content_encoded = base64.b64encode(new_file_content.encode('utf-8')).decode('utf-8')

    payload = {
        "message": commit_message,
        "content": new_content_encoded,
        "sha": sha,
    }
    return requests.put(url, headers=headers, json=payload, timeout=15)


def update_players_file(gh_repo: str, gh_token: str, mutate_fn, commit_message: str):
    """
    Читает players.js, применяет mutate_fn(players_list) -> players_list
    (мутирует список игроков как угодно), пишет обратно.

    При конфликте sha (файл изменился между чтением и записью - например
    два тестера одновременно вносят результаты) повторяет попытку до
    MAX_RETRIES раз: перечитывает файл заново и снова накатывает mutate_fn
    поверх свежих данных, чтобы не потерять чужие изменения.

    Возвращает players_list (уже с применённым изменением) при успехе.
    Бросает GithubStorageError, если все попытки исчерпаны.
    """
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            players_list, sha, prefix, suffix = _get_file(gh_repo, gh_token)
            players_list = mutate_fn(players_list)

            put_response = _put_file(gh_repo, gh_token, players_list, sha, prefix, suffix, commit_message)

            if put_response.status_code in (200, 201):
                return players_list

            if put_response.status_code in (409, 422):
                # sha конфликт - файл изменился, пробуем ещё раз с чистого листа
                last_error = f"sha-конфликт (попытка {attempt}/{MAX_RETRIES})"
                time.sleep(RETRY_DELAY_SECONDS)
                continue

            raise GithubStorageError(f"Ошибка записи на GitHub: {put_response.status_code} {put_response.text[:200]}")

        except GithubStorageError:
            raise
        except requests.RequestException as e:
            last_error = f"Сетевая ошибка: {e}"
            time.sleep(RETRY_DELAY_SECONDS)
            continue

    raise GithubStorageError(f"Не удалось записать после {MAX_RETRIES} попыток. Последняя причина: {last_error}")
