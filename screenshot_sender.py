import os
import json
import requests
import subprocess
from pynput import keyboard
from datetime import datetime
import platform

# Загружаем конфиг
CONFIG_PATH = "config.json"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print("❌ Ошибка: config.json не найден!")
        exit(1)
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

config = load_config()
TOKEN = config["telegram"]["bot_token"]
CHAT_ID = config["telegram"]["chat_id"]
API_URL = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
HOTKEY = config["screenshot"]["hotkey"].lower().split("+")
OS_TYPE = config["screenshot"].get("os", "auto")

# Автоопределение ОС
if OS_TYPE == "auto":
    system_platform = platform.system().lower()
    if "linux" in system_platform:
        OS_TYPE = "ubuntu"
    elif "darwin" in system_platform:
        OS_TYPE = "macos"
    elif "windows" in system_platform:
        OS_TYPE = "windows"
    else:
        print("❌ Ошибка: Неизвестная ОС.")
        exit(1)

COMMANDS = config["screenshot"]["commands"].get(OS_TYPE, {})
SCREENSHOTS_DIR = os.path.expanduser("~/Pictures/Screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)  # ✅ Создаем папку, если её нет

def take_screenshot():
    """Делает скриншот и возвращает путь к файлу."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(SCREENSHOTS_DIR, f"screenshot_{timestamp}.png")

        run_command = COMMANDS.get("run", "").strip()
        print(f"🖥️ ОС: {OS_TYPE}")
        print(f"🛠 RUN-команда: {run_command}")

        if not run_command:
            print("❌ Ошибка: команда для скриншота не указана в config.json.")
            return None

        subprocess.run(
            ["/bin/bash", "-c", f'{run_command} "{screenshot_path}"'],
            check=True,
            env=os.environ,
        )

        if os.path.exists(screenshot_path):
            print(f"📸 Скриншот сохранен: {screenshot_path}")
            return screenshot_path
        else:
            print("❌ Ошибка: скриншот не был создан!")
            return None

    except subprocess.CalledProcessError as e:
        print(f"⚠ Ошибка при создании скриншота: {e}")
        return None


def send_screenshot(filename):
    """Отправляет скриншот в Telegram и удаляет файл после отправки."""
    try:
        with open(filename, "rb") as img:
            response = requests.post(
                API_URL, data={"chat_id": CHAT_ID}, files={"photo": img}
            )
        if response.status_code == 200:
            print(f"📤 Скриншот {filename} успешно отправлен!")
            os.remove(filename)
            print(f"🗑️ Скриншот {filename} удален после отправки.")
        else:
            print(f"❌ Ошибка отправки: {response.text}")
    except Exception as e:
        print(f"⚠ Ошибка при отправке: {e}")


def on_press(key):
    """Обработка нажатия горячей клавиши."""
    try:
        key_str = (
            key.char.lower()
            if hasattr(key, "char") and key.char
            else str(key).split(".")[-1].lower()
        )
        pressed_keys.add(key_str)

        if set(HOTKEY).issubset(pressed_keys):
            print("📸 Горячая клавиша нажата! Делаю скриншот...")
            screenshot = take_screenshot()
            if screenshot:
                send_screenshot(screenshot)
            pressed_keys.clear()

    except Exception as e:
        print(f"⚠ Ошибка обработки клавиши: {e}")


def on_release(key):
    """Очищает состояние клавиш при отпускании."""
    try:
        key_str = (
            key.char.lower()
            if hasattr(key, "char") and key.char
            else str(key).split(".")[-1].lower()
        )
        pressed_keys.discard(key_str)
    except Exception as e:
        print(f"⚠ Ошибка при отпускании клавиши: {e}")


pressed_keys = set()

print(f"🚀 Скрипт запущен. Ожидание горячей клавиши {'+'.join(HOTKEY)}...")
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
