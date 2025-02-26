import os
import json
import subprocess
from datetime import datetime
import requests
from ai_api import process_image  # Используем существующую обработку
import asyncio

# 🔹 Загружаем конфиг
with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["telegram"]["bot_token"]
CHAT_ID = config["telegram"]["chat_id"]
PHOTO_URL = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
SESSION_DIR = "session_temp"
os.makedirs(SESSION_DIR, exist_ok=True)


async def take_screenshot():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(SESSION_DIR, f"screenshot_{timestamp}.png")
    subprocess.run(f"gnome-screenshot -f {screenshot_path}", shell=True)
    return screenshot_path if os.path.exists(screenshot_path) else None


async def process_and_send(screenshot):
    print(f"📸 Скриншот сделан: {screenshot}")
    print("🧠 Обработка через OpenAI...")

    # ✅ Обработка локально через ИИ
    result = await process_image(screenshot)
    print(f"🤖 Ответ ИИ: {result}")

    # ✅ Отправка в Telegram
    with open(screenshot, "rb") as img:
        response = requests.post(
            PHOTO_URL,
            data={"chat_id": CHAT_ID, "caption": f"🤖 Ответ ИИ:\n{result}"},
            files={"photo": img},
        )
    if response.status_code == 200:
        print("✅ Результат успешно отправлен в Telegram.")
    else:
        print(f"❌ Ошибка при отправке в Telegram: {response.text}")

    # ✅ Удаление скрина
    os.remove(screenshot)
    print(f"🗑️ Скриншот {screenshot} удален после обработки.")


async def main():
    """🚀 Основной цикл обработки скринов до нового запуска."""
    print(
        f"🚀 Сессия обработки началась. Ожидаем горячую клавишу {config['screenshot']['hotkey']}..."
    )
    from pynput import keyboard

    pressed_keys = set()
    HOTKEY = config["screenshot"]["hotkey"].lower().split("+")

    def on_press(key):
        try:
            key_str = (
                key.char.lower()
                if hasattr(key, "char") and key.char
                else str(key).split(".")[-1].lower()
            )
            pressed_keys.add(key_str)
            if set(HOTKEY).issubset(pressed_keys):
                print("📸 Горячая клавиша нажата! Обработка...")
                screenshot = asyncio.run(take_screenshot())
                asyncio.run(process_and_send(screenshot))
                pressed_keys.clear()
        except Exception as e:
            print(f"⚠ Ошибка: {e}")

    def on_release(key):
        key_str = (
            key.char.lower()
            if hasattr(key, "char") and key.char
            else str(key).split(".")[-1].lower()
        )
        pressed_keys.discard(key_str)

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    # ✅ Очистка прошлой сессии
    for file in os.listdir(SESSION_DIR):
        os.remove(os.path.join(SESSION_DIR, file))
    print(f"🧹 Папка {SESSION_DIR} очищена перед стартом новой сессии.")
    asyncio.run(main())
