import os
import subprocess
import logging
import time
from datetime import datetime
from src.config_handler import ConfigHandler


# Функция перевода строк
def translate(text):
    return ConfigHandler.translate(text)


# Определение папки для хранения скриншотов
SESSION_DIR = os.path.abspath("logs/session_temp")
os.makedirs(SESSION_DIR, exist_ok=True)

# Загружаем команды flameshot из config.json
FLAMESHOT_CONFIG = ConfigHandler.get_value("screenshot.commands.flameshot", {})

INSTALL_CMD = FLAMESHOT_CONFIG.get("install", "")
CHECK_CMD = FLAMESHOT_CONFIG.get("check", "")
SCREENSHOT_CMD = FLAMESHOT_CONFIG.get("run", "")

if not INSTALL_CMD or not CHECK_CMD or not SCREENSHOT_CMD:
    logging.error(translate("Ошибка: отсутствуют команды для flameshot в config.json!"))
    exit(1)


# Проверка установки flameshot
def check_flameshot_installed():
    try:
        subprocess.run(
            CHECK_CMD,
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


# Установка flameshot, если нет
def install_flameshot():
    logging.warning(translate("Flameshot не найден, выполняю установку..."))
    try:
        subprocess.run(INSTALL_CMD, shell=True, check=True)
        logging.info(translate("Flameshot успешно установлен."))
    except subprocess.CalledProcessError:
        logging.error(translate("Ошибка установки flameshot! Установите его вручную."))


# Делает скриншот с flameshot и возвращает путь к файлу
def take_screenshot():
    if not check_flameshot_installed():
        install_flameshot()
        if not check_flameshot_installed():
            logging.error(
                translate("Flameshot не установлен. Скриншот не может быть создан.")
            )
            return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(SESSION_DIR, f"screenshot_{timestamp}.png")

    try:
        command = SCREENSHOT_CMD.replace("screenshot.png", screenshot_path)

        logging.info(translate("Выполняю команду:") + f" {command}")
        subprocess.run(command, shell=True, check=True)
        subprocess.run("wtype Shift", shell=True, check=False)

        start_time = time.time()
        while not os.path.exists(screenshot_path):
            if time.time() - start_time > 3:
                logging.error(
                    translate("Файл не найден после скриншота:") + f" {screenshot_path}"
                )
                return None
            time.sleep(0.1)

        logging.info(translate("Скриншот сохранен:") + f" {screenshot_path}")
        return screenshot_path

    except subprocess.CalledProcessError as e:
        logging.error(translate("Ошибка при создании скриншота:") + f" {e}")
        return None
