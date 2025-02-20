import json
import telebot
import os
import requests
import time

# Загрузка конфигурации
CONFIG_PATH = "config.json"


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"telegram": {}}
    with open(CONFIG_PATH, "r") as config_file:
        return json.load(config_file)


def save_config(config):
    with open(CONFIG_PATH, "w") as config_file:
        json.dump(config, config_file, indent=4)
    print("✅ chat_id успешно записан в config.json!")


def get_chat_id(token):
    """Получает chat_id через getUpdates"""
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        response = requests.get(url).json()
        if "result" in response and len(response["result"]) > 0:
            chat_id = response["result"][-1]["message"]["chat"]["id"]
            print(f"🔹 Автоматически получен chat_id: {chat_id}")
            return chat_id
    except Exception as e:
        print(f"⚠ Ошибка получения chat_id: {e}")
    return None


config = load_config()
TOKEN = config.get("telegram", {}).get("bot_token")
CHAT_ID = config.get("telegram", {}).get("chat_id")

# Проверяем наличие bot_token
if not TOKEN:
    print("❌ Ошибка: bot_token не найден в config.json!")
    exit(1)

# Если chat_id отсутствует, получаем его через API
if not CHAT_ID:
    print("🔹 Определяем chat_id...")
    CHAT_ID = get_chat_id(TOKEN)
    if CHAT_ID:
        config["telegram"]["chat_id"] = CHAT_ID
        save_config(config)
    else:
        print(
            "⚠ Не удалось получить chat_id. Отправьте /start боту и попробуйте снова."
        )

# Запуск бота
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "👋 Привет! Отправь мне изображение, и я его обработаю.")

    # Если chat_id еще не записан, сохраняем его
    if not config["telegram"].get("chat_id"):
        config["telegram"]["chat_id"] = chat_id
        save_config(config)
        print(f"✅ chat_id {chat_id} автоматически сохранен!")


@bot.message_handler(content_types=["photo"])
def handle_screenshot(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open("received.png", "wb") as img:
        img.write(downloaded_file)

    bot.send_message(message.chat.id, "✅ Изображение получено!")


bot.polling()
