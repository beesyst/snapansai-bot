import os
import subprocess
import requests
import asyncio
import logging
from datetime import datetime
from src.ai_api import process_image
from src.config_handler import ConfigHandler
from pynput import keyboard


# Функция перевода строк
def translate(text):
    return ConfigHandler.translate(text)


# Определение пути
SESSION_DIR = "logs/session_temp"

logging.info(f"SESSION_DIR: {SESSION_DIR}")

TOKEN = ConfigHandler.get_value("telegram.bot_token")
CHAT_ID = ConfigHandler.get_value("telegram.chat_id")
PHOTO_URL = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

# Определение ОС и команды для скриншотов
OS_TYPE = ConfigHandler.get_value("screenshot.os", "unknown")
SCREENSHOT_CMD = ConfigHandler.get_value(f"screenshot.commands.{OS_TYPE}.run", "")

if not SCREENSHOT_CMD:
    logging.error(translate("Ошибка: Неизвестная ОС. Укажите 'os' в config.json."))
    exit(1)

# Флаг от множественных вызовов
processing = False


# Функция снятия скрина
async def take_screenshot():
    global processing
    if processing:
        logging.info(
            translate("Уже выполняется обработка, повторное нажатие игнорируется.")
        )
        return None

    processing = True
    os.makedirs(SESSION_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(SESSION_DIR, f"screenshot_{timestamp}.png")

    try:
        command = SCREENSHOT_CMD.replace("screenshot.png", screenshot_path)
        subprocess.run(command, shell=True, check=True)

        if os.path.exists(screenshot_path):
            logging.info(f"{translate('Скриншот сделан:')} {screenshot_path}")
            return screenshot_path
    except subprocess.CalledProcessError as e:
        logging.error(f"{translate('Ошибка при создании скриншота:')} {e}")

    processing = False
    return None


# Функция обработки и отправки скрина
async def process_and_send(screenshot):
    global processing
    try:
        logging.info(translate("Обработка изображения через ИИ..."))
        result = await process_image(screenshot)
        logging.info(f"{translate('Ответ ИИ:')}\n{result}")

        with requests.Session() as session:
            with open(screenshot, "rb") as img:
                response = session.post(
                    PHOTO_URL,
                    data={"chat_id": CHAT_ID, "caption": result},
                    files={"photo": img},
                )

        if response.status_code == 200:
            logging.info(translate("Результат успешно отправлен в Telegram."))
        else:
            logging.error(f"{translate('Ошибка при отправке:')} {response.text}")

        os.remove(screenshot)
        logging.info(f"{translate('Скриншот удален:')} {screenshot}")
    except Exception as e:
        logging.error(f"{translate('Ошибка при обработке или отправке:')} {e}")
    processing = False


# Основной цикл обработки горячих клавиш
async def main():
    logging.info(
        f"{translate('Ожидаем горячие клавиши:')} {ConfigHandler.get_value('screenshot.hotkey')}"
    )

    pressed_keys = set()

    # Читаем горячие клавиши из конфига
    hotkeys_raw = ConfigHandler.get_value("screenshot.hotkey", "alt+s")
    hotkey_sets = [set(hk.strip().lower().split("+")) for hk in hotkeys_raw.split(",")]

    loop = asyncio.get_running_loop()

    async def on_trigger():
        screenshot = await take_screenshot()
        if screenshot:
            await process_and_send(screenshot)
        pressed_keys.clear()

    def on_press(key):
        try:
            key_str = (
                key.char.lower()
                if hasattr(key, "char") and key.char
                else str(key).split(".")[-1].lower()
            )
            pressed_keys.add(key_str)

            # Проверяем, совпадает ли какая-то комбинация
            for hotkey in hotkey_sets:
                if hotkey.issubset(pressed_keys):
                    logging.info(
                        translate("Горячая клавиша нажата! Запускаю обработку...")
                    )
                    asyncio.run_coroutine_threadsafe(on_trigger(), loop)
                    break
        except Exception as e:
            logging.error(f"{translate('Ошибка в обработке нажатия:')} {e}")

    def on_release(key):
        key_str = (
            key.char.lower()
            if hasattr(key, "char") and key.char
            else str(key).split(".")[-1].lower()
        )
        pressed_keys.discard(key_str)

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        await asyncio.get_running_loop().run_in_executor(None, listener.join)


# Запуск
if __name__ == "__main__":
    asyncio.run(main())
