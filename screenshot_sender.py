import os
import json
import subprocess
from datetime import datetime
import requests
import asyncio
from ai_api import process_image
from pynput import keyboard
import logging

# Логирование
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Загрузка конфига
with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["telegram"]["bot_token"]
CHAT_ID = config["telegram"]["chat_id"]
PHOTO_URL = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
SESSION_DIR = "session_temp"
os.makedirs(SESSION_DIR, exist_ok=True)

# Скриншот
async def take_screenshot():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(SESSION_DIR, f"screenshot_{timestamp}.png")
    subprocess.run(f"gnome-screenshot -f {screenshot_path}", shell=True)
    if os.path.exists(screenshot_path):
        logging.info(f"📸 Скриншот сделан: {screenshot_path}")
        return screenshot_path
    else:
        logging.error("❌ Ошибка при создании скриншота.")
        return None

# Обработка и отправка скрина
async def process_and_send(screenshot):
    try:
        logging.info("🧠 Обработка изображения через ИИ...")
        result = await process_image(screenshot)
        logging.info(f"🤖 Ответ ИИ: {result}")

        with requests.Session() as session:
            with open(screenshot, "rb") as img:
                response = session.post(
                    PHOTO_URL,
                    data={"chat_id": CHAT_ID, "caption": f"🤖 Ответ ИИ:\n{result}"},
                    files={"photo": img},
                )
        if response.status_code == 200:
            logging.info("✅ Результат успешно отправлен в Telegram.")
        else:
            logging.error(f"❌ Ошибка при отправке: {response.text}")

        if os.path.exists(screenshot):
            os.remove(screenshot)
            logging.info(f"🗑️ Скриншот {screenshot} удален.")
    except Exception as e:
        logging.error(f"⚠ Ошибка при обработке или отправке: {e}")

# Основной цикл обработки горячих клавиш
async def main():
    logging.info(f"🚀 Ожидаем горячую клавишу: {config['screenshot']['hotkey']}...")
    pressed_keys = set()
    HOTKEY = set(config["screenshot"]["hotkey"].lower().split("+"))

    loop = asyncio.get_event_loop()

    async def on_trigger():
        screenshot = await take_screenshot()
        if screenshot:
            await process_and_send(screenshot)
        pressed_keys.clear()

    def on_press(key):
        try:
            key_str = (
                key.char.lower() if hasattr(key, "char") and key.char else str(key).split(".")[-1].lower()
            )
            pressed_keys.add(key_str)
            if HOTKEY.issubset(pressed_keys):
                logging.info("📸 Горячая клавиша нажата! Запускаю обработку...")
                asyncio.run_coroutine_threadsafe(on_trigger(), loop)
        except Exception as e:
            logging.error(f"⚠ Ошибка в обработке нажатия: {e}")

    def on_release(key):
        key_str = (
            key.char.lower() if hasattr(key, "char") and key.char else str(key).split(".")[-1].lower()
        )
        pressed_keys.discard(key_str)

    # Очистка предыдущих скриншотов
    for file in os.listdir(SESSION_DIR):
        try:
            os.remove(os.path.join(SESSION_DIR, file))
        except Exception as e:
            logging.error(f"⚠ Ошибка удаления {file}: {e}")
    logging.info(f"🧹 Папка {SESSION_DIR} очищена.")

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        await asyncio.get_event_loop().run_in_executor(None, listener.join)

if __name__ == "__main__":
    asyncio.run(main())
