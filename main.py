import os
import re
import json
import base64
import requests
import telebot
import math
from threading import Thread
from flask import Flask

# Крошечный веб-сервер для обмана Render
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Считываем настройки из секретных переменных Render
TG_TOKEN = os.environ.get('TG_TOKEN')
GH_TOKEN = os.environ.get('GH_TOKEN')
GH_REPO = os.environ.get('GH_REPO')

bot = telebot.TeleBot(TG_TOKEN)

TARGET_CHAT_ID = -1003257860755
TARGET_THREAD_ID = 11

VALID_KITS = [
    "Hardcore", "Combo", "Emerald Pot", "RVM", "Emerald", "Beast", "Vanilla", 
    "Dragonhide", "Pickaxe", "Crystal", "Mace", "Gapple", "SMP", "Manhunt", "Diamond"
]

# Веса рангов для вычисления среднего тира (1 - 10)
TIER_WEIGHTS = {
    'HT1': 10, 'LT1': 9,
    'HT2': 8,  'LT2': 7,
    'HT3': 6,  'LT3': 5,
    'HT4': 4,  'LT4': 3,
    'HT5': 2,  'LT5': 1
}

# Обратный поиск названия ранга по его весу
REVERSE_WEIGHTS = {
    10: 'HT1', 9: 'LT1',
    8: 'HT2',  7: 'LT2',
    6: 'HT3',  5: 'LT3',
    4: 'HT4',  3: 'LT4',
    2: 'HT5',  1: 'LT5'
}

# Очки для расчета разницы (PTS) на конкретном ките
TIER_POINTS = {
    'HT1': 100, 'LT1': 90,
    'HT2': 80,  'LT2': 70,
    'HT3': 60,  'LT3': 50,
    'HT4': 40,  'LT4': 30,
    'HT5': 20,  'LT5': 10,
    'UNRANKED': 0
}

# Порядок возрастания тиров для вычисления следующего ранга на одном ките
TIER_ORDER = ['UNRANKED', 'LT5', 'HT5', 'LT4', 'HT4', 'LT3', 'HT3', 'LT2', 'HT2', 'LT1', 'HT1']

def get_next_tier_info(current_tier):
    """Вычисляет следующий тир для кита и сколько PTS до него не хватает"""
    clean_tier = current_tier.upper().strip()
    if clean_tier not in TIER_ORDER:
        return None, 0
    
    current_idx = TIER_ORDER.index(clean_tier)
    if current_idx == len(TIER_ORDER) - 1:
        return None, 0
        
    next_tier = TIER_ORDER[current_idx + 1]
    pts_needed = TIER_POINTS[next_tier] - TIER_POINTS[clean_tier]
    return next_tier, pts_needed

def calculate_overall_tier(player_tiers):
    """
    Рассчитывает средний ранг по всем пройденным тестам
    """
    total_weight = 0
    count = 0
    
    for kit_name, tier_val in player_tiers.items():
        # Если тир записан как объект, достаем из него строку
        if isinstance(tier_val, dict):
            tier_str = tier_val.get('tier', 'UNRANKED').upper()
        else:
            tier_str = str(tier_val).upper()
            
        if tier_str.startswith('R') and len(tier_str) > 1:
            tier_str = tier_str[1:] # Срезаем "R" для Retired рангов
            
        if tier_str in TIER_WEIGHTS:
            total_weight += TIER_WEIGHTS[tier_str]
            count += 1
            
    if count == 0:
        return "Unranked", 0

    # Текущий средний вес (с округлением Math.round)
    avg_weight = int(round(total_weight / count))
    current_overall = REVERSE_WEIGHTS.get(avg_weight, "Unranked")
    
    return current_overall, count

@bot.message_handler(func=lambda message: message.chat.id == TARGET_CHAT_ID and message.message_thread_id == TARGET_THREAD_ID)
def handle_telegram_message(message):
    if "Игрок:" not in message.text or "Кит:" not in message.text or "Полученный ранг:" not in message.text:
        return

    text = message.text
    try:
        player_name = re.search(r"Игрок:\s*([^\n]+)", text).group(1).strip()
        kit_name = re.search(r"Кит:\s*([^\n]+)", text).group(1).strip()
        region = re.search(r"Регион:\s*([^\n]+)", text).group(1).strip().upper()
        device = re.search(r"Устройство:\s*([^\n]+)", text).group(1).strip().upper()
        new_tier = re.search(r"Полученный ранг:\s*([^\n]+)", text).group(1).strip().upper()
    except AttributeError:
        bot.reply_to(message, "❌ **Ошибка. Не удалось распознать шаблон. Проверьте правильность заполнения полей.**", parse_mode="Markdown")
        return

    matched_kit = next((k for k in VALID_KITS if k.lower() == kit_name.lower()), None)
    if not matched_kit:
        matched_kit = kit_name

    # 1. ОТПРАВЛЯЕМ СООБЩЕНИЕ-ЗАГРУЗКУ (БЕЗ СМАЙЛИКОВ И ВОСКЛИЦАТЕЛЬНЫХ ЗНАКОВ)
    status_msg = bot.reply_to(message, f"**Обрабатываю результат для {player_name}...**", parse_mode="Markdown")

    file_path = "players/players.js"
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{file_path}"
    headers = {"Authorization": f"token {GH_TOKEN}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                text=f"❌ **Ошибка GitHub при чтении файла: {response.status_code}**",
                parse_mode="Markdown"
            )
            return

        file_data = response.json()
        sha = file_data['sha']
        content = base64.b64decode(file_data['content']).decode('utf-8')

        json_array_match = re.search(r"=\s*(\[.*\]);?\s*$", content, re.DOTALL)
        if not json_array_match:
            json_array_match = re.search(r"(\[.*\])", content, re.DOTALL)
            if not json_array_match:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    text="❌ **Ошибка: Не удалось найти структуру массива в файле.**",
                    parse_mode="Markdown"
                )
                return

        raw_json_text = json_array_match.group(1)
        valid_json_text = re.sub(r'(\s*)(\w+)(\s*):', r'\1"\2"\3:', raw_json_text)
        
        try:
            players_list = json.loads(valid_json_text)
        except json.JSONDecodeError as je:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                text=f"❌ **Ошибка JSON после обработки: {str(je)}**",
                parse_mode="Markdown"
            )
            return

        player_found = False
        active_player_tiers = {}
        
        for player in players_list:
            if player.get('name', '').lower() == player_name.lower():
                player['name'] = player_name 
                player['region'] = region
                player['device'] = device
                if 'tiers' not in player:
                    player['tiers'] = {}
                player['tiers'][matched_kit] = new_tier
                active_player_tiers = player['tiers']
                player_found = True
                break

        if not player_found:
            new_player = {
                "name": player_name,
                "region": region,
                "device": device,
                "tiers": {matched_kit: new_tier}
            }
            players_list.append(new_player)
            active_player_tiers = new_player['tiers']

        new_json_array = json.dumps(players_list, indent=4, ensure_ascii=False)
        new_js_array = re.sub(r'"(\w+)"\s*:', r'\1:', new_json_array)
        
        prefix = content.split('[')[0]
        suffix = ";" if content.strip().endswith(';') else ""
        
        new_file_content = f"{prefix}{new_js_array}{suffix}"
        new_content_encoded = base64.b64encode(new_file_content.encode('utf-8')).decode('utf-8')

        payload = {
            "message": f"auto update tier: {player_name} -> {matched_kit} ({new_tier})",
            "content": new_content_encoded,
            "sha": sha
        }

        put_response = requests.put(url, headers=headers, json=payload)

        if put_response.status_code in [200, 201]:
            # Расчет разницы на конкретном ките
            next_tier, pts_needed = get_next_tier_info(new_tier)
            if next_tier:
                kit_progress_text = f"**До следующего ранга на {matched_kit} [{next_tier}] осталось: {pts_needed} PTS**"
            else:
                kit_progress_text = f"**На ките {matched_kit} достигнут максимальный ранг**"

            # Расчет общего среднего ранга по ВСЕМ китам игрока
            overall_tier, tests_count = calculate_overall_tier(active_player_tiers)

            # Собираем полностью ЖИРНЫЙ текст ответа без смайликов, восклицательных знаков и строки main+sub прогресса
            success_text = (
                f"**Игрок {player_name} внесен в базу данных**\n\n"
                f"**Регион: {region} | Устройство: {device}**\n"
                f"**Кит: {matched_kit} | Ранг: {new_tier}**\n\n"
                f"**Текущий средний ранг: {overall_tier} [Тестов: {tests_count}]**\n"
                f"**{kit_progress_text}**"
            )

            # 2. РЕДАКТИРУЕМ СООБЩЕНИЕ НА ШАБЛОН УСПЕХА
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                text=success_text,
                parse_mode="Markdown"
            )
        else:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                text=f"❌ **Ошибка записи на GitHub: {put_response.status_code}**",
                parse_mode="Markdown"
            )

    except Exception as e:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            text=f"❌ **Системная ошибка: {str(e)}**",
            parse_mode="Markdown"
        )

if __name__ == '__main__':
    print("Запуск веб-сервера для Render...")
    t = Thread(target=run_web_server)
    t.start()
    
    print("Бот успешно запущен и защищен. Ожидаю результаты...")
    bot.infinity_polling()