import os
import requests
import asyncio
import logging
from src.ai_api import process_image
from src.config_handler import ConfigHandler
from pynput import keyboard

# Подключение модуля flameshot
METHOD = ConfigHandler.get_value("screenshot.method", "default")
if METHOD == "flameshot":
    from methods.flameshot import take_screenshot
else:
    import subprocess
    from datetime import datetime


# Функция перевода строк
def translate(text):
    return ConfigHandler.translate(text)


# Определение пути
SESSION_DIR = os.path.abspath("logs/session_temp")
os.makedirs(SESSION_DIR, exist_ok=True)

logging.info(f"SESSION_DIR: {SESSION_DIR}")

TOKEN = ConfigHandler.get_value("telegram.bot_token")
CHAT_ID = ConfigHandler.get_value("telegram.chat_id")
PHOTO_URL = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

logging.info(translate("Используется метод скриншотов:") + f" {METHOD}")

# Если метод "default", выбираем метод ОС
if METHOD == "default":
    OS_TYPE = ConfigHandler.get_value("screenshot.os", "unknown")
    METHOD = OS_TYPE

# Для всех методов, кроме flameshot, получаем команды из config.json
if METHOD != "flameshot":
    INSTALL_CMD = ConfigHandler.get_value(f"screenshot.commands.{METHOD}.install", "")
    CHECK_CMD = ConfigHandler.get_value(f"screenshot.commands.{METHOD}.check", "")
    SCREENSHOT_CMD = ConfigHandler.get_value(f"screenshot.commands.{METHOD}.run", "")

    if not SCREENSHOT_CMD:
        logging.error(
            translate("Ошибка: Метод {method} не найден в config.json!").replace(
                "{method}", METHOD
            )
        )
        exit(1)

    if CHECK_CMD:
        try:
            subprocess.run(
                CHECK_CMD,
                shell=True,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            logging.warning(
                translate("Метод {method} не найден, выполняю установку...").replace(
                    "{method}", METHOD
                )
            )
            if INSTALL_CMD:
                subprocess.run(INSTALL_CMD, shell=True, check=True)
            else:
                logging.error(
                    translate("Ошибка: Установка для {method} не определена.").replace(
                        "{method}", METHOD
                    )
                )
                exit(1)


# Функция снятия скрина
async def take_screenshot_generic():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(SESSION_DIR, f"screenshot_{timestamp}.png")

    try:
        command = SCREENSHOT_CMD.replace("screenshot.png", screenshot_path)
        subprocess.run(command, shell=True, check=True)
        await asyncio.sleep(1)

        if os.path.exists(screenshot_path):
            logging.info(translate("Скриншот сделан:") + f" {screenshot_path}")
            return screenshot_path
    except subprocess.CalledProcessError as e:
        logging.error(
            translate("Ошибка при создании скриншота: {error}").replace(
                "{error}", str(e)
            )
        )
    return None


# Определяем, какой метод использовать
async def take_screenshot_dispatcher():
    if METHOD == "flameshot":
        return take_screenshot()
    return await take_screenshot_generic()


# Функция обработки и отправки скрина
async def process_and_send(screenshot):
    try:
        logging.info(translate("Обработка изображения через ИИ..."))
        result = await process_image(screenshot)
        logging.info(translate("Ответ ИИ:") + f"\n{result}")
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
            logging.error(translate("Ошибка при отправке:") + f" {response.text}")
    except Exception as e:
        logging.error(translate("Ошибка при обработке или отправке:") + f" {e}")
    finally:
        if os.path.exists(screenshot):
            os.remove(screenshot)
            logging.info(translate("Скриншот удален:") + f" {screenshot}")


# Основной цикл обработки горячих клавиш
async def main():
    logging.info(
        translate("Ожидание горячих клавиш:")
        + f" {ConfigHandler.get_value('screenshot.hotkey')}"
    )

    pressed_keys = set()

    hotkeys_raw = ConfigHandler.get_value("screenshot.hotkey", "alt+s")
    hotkey_sets = [set(hk.strip().lower().split("+")) for hk in hotkeys_raw.split(",")]

    loop = asyncio.get_running_loop()

    async def on_trigger():
        screenshot = await take_screenshot_dispatcher()
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

            for hotkey in hotkey_sets:
                if hotkey.issubset(pressed_keys):
                    logging.info(
                        translate("Горячая клавиша нажата. Запускаю обработку...")
                    )
                    asyncio.run_coroutine_threadsafe(on_trigger(), loop)
                    break
        except Exception as e:
            logging.error(
                translate("Ошибка в обработке нажатия: {error}").replace(
                    "{error}", str(e)
                )
            )

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
