import os
import re
import json
import base64
import requests
import telebot

# Считываем настройки из секретных переменных Render
TG_TOKEN = os.environ.get('TG_TOKEN')
GH_TOKEN = os.environ.get('GH_TOKEN')
GH_REPO = os.environ.get('GH_REPO')  # Формат: "ваш_логин/имя_репозитория"

bot = telebot.TeleBot(TG_TOKEN)

# Список всех ваших 15 китов для проверки
VALID_KITS = [
    "Hardcore", "Combo", "Emerald Pot", "RVM", "Emerald", "Beast", "Vanilla", 
    "Dragonhide", "Pickaxe", "Crystal", "Mace", "Gapple", "SMP", "Manhunt", "Diamond"
]

@bot.message_handler(func=lambda message: True)
def handle_telegram_message(message):
    # Бот реагирует только на сообщения, содержащие ключевые поля шаблона
    if "Игрок:" not in message.text or "Кит:" not in message.text or "Полученный ранг:" not in message.text:
        return

    text = message.text
    try:
        # Извлекаем данные из вашего шаблона результатов
        player_name = re.search(r"Игрок:\s*([^\n]+)", text).group(1).strip()
        kit_name = re.search(r"Кит:\s*([^\n]+)", text).group(1).strip()
        region = re.search(r"Регион:\s*([^\n]+)", text).group(1).strip().upper()
        device = re.search(r"Устройство:\s*([^\n]+)", text).group(1).strip().upper()
        new_tier = re.search(r"Полученный ранг:\s*([^\n]+)", text).group(1).strip().upper()
    except AttributeError:
        bot.reply_to(message, "❌ Ошибка! Не удалось распознать шаблон. Проверьте правильность заполнения полей.")
        return

    # Проверяем имя кита (игнорируя регистр букв)
    matched_kit = next((k for k in VALID_KITS if k.lower() == kit_name.lower()), None)
    if not matched_kit:
        bot.reply_to(message, f"⚠️ Предупреждение: Кит '{kit_name}' не найден в официальном списке, но я попробую внести как есть.")
        matched_kit = kit_name

    # ПУТЬ К ФАЙЛУ: Если players.js лежит прямо в корне, оставляем так.
    file_path = "players/players.js"
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{file_path}"
    headers = {"Authorization": f"token {GH_TOKEN}"}

    bot.reply_to(message, f"⏳ Обрабатываю результат для **{player_name}**...")

    try:
        # 1. Запрашиваем текущий файл players.js с GitHub
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            bot.reply_to(message, f"❌ Ошибка GitHub при чтении файла: {response.status_code}")
            return

        file_data = response.json()
        sha = file_data['sha']
        content = base64.b64decode(file_data['content']).decode('utf-8')

        # 2. Находим массив внутри структуры `const players = [ ... ];`
        json_array_match = re.search(r"=\s*(\[.*\]);?\s*$", content, re.DOTALL)
        if not json_array_match:
            json_array_match = re.search(r"(\[.*\])", content, re.DOTALL)
            if not json_array_match:
                bot.reply_to(message, "❌ Ошибка: Не удалось найти структуру массива в файле.")
                return

        raw_json_text = json_array_match.group(1)
        
        try:
            players_list = json.loads(raw_json_text)
        except json.JSONDecodeError as je:
            bot.reply_to(message, f"❌ Ошибка JSON: {str(je)}\nУбедитесь, что в файле players.js ВСЕ ключи и строки используют ДВОЙНЫЕ кавычки.")
            return

        # 3. Ищем игрока в списке (без учета регистра букв)
        player_found = False
        for player in players_list:
            if player.get('name', '').lower() == player_name.lower():
                player['name'] = player_name 
                player['region'] = region
                player['device'] = device
                if 'tiers' not in player:
                    player['tiers'] = {}
                player['tiers'][matched_kit] = new_tier
                player_found = True
                break

        # Если игрока нет в базе, создаем для него новую запись в самом низу
        if not player_found:
            new_player = {
                "name": player_name,
                "region": region,
                "device": device,
                "tiers": {matched_kit: new_tier}
            }
            players_list.append(new_player)

        # 4. Собираем структуру файла обратно в формат JavaScript
        new_json_array = json.dumps(players_list, indent=4, ensure_ascii=False)
        prefix = content.split('[')[0]
        suffix = ";" if content.strip().endswith(';') else ""
        
        new_file_content = f"{prefix}{new_json_array}{suffix}"
        new_content_encoded = base64.b64encode(new_file_content.encode('utf-8')).decode('utf-8')

        # 5. Отправляем обновленный файл обратно на GitHub
        payload = {
            "message": f"auto update tier: {player_name} -> {matched_kit} ({new_tier})",
            "content": new_content_encoded,
            "sha": sha
        }

        put_response = requests.put(url, headers=headers, json=payload)

        if put_response.status_code in [200, 201]:
            bot.reply_to(message, f"✅ Успешно! Результат игрока **{player_name}** добавлен в базу.\nКит: {matched_kit} | Ранг: {new_tier}")
        else:
            bot.reply_to(message, f"❌ Ошибка записи на GitHub: {put_response.status_code}")

    except Exception as e:
        bot.reply_to(message, f"❌ Системная ошибка: {str(e)}")

if __name__ == '__main__':
    print("Бот успешно запущен и ожидает результаты...")
    bot.infinity_polling()
