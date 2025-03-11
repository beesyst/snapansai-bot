import os
import subprocess
import logging
import time
from datetime import datetime
from src.config_handler import ConfigHandler

# Определение папки для хранения скриншотов
SESSION_DIR = os.path.abspath("logs/session_temp")
os.makedirs(SESSION_DIR, exist_ok=True)

# Загружаем команды flameshot из config.json
FLAMESHOT_CONFIG = ConfigHandler.get_value("screenshot.commands.flameshot", {})

INSTALL_CMD = FLAMESHOT_CONFIG.get("install", "")
CHECK_CMD = FLAMESHOT_CONFIG.get("check", "")
SCREENSHOT_CMD = FLAMESHOT_CONFIG.get("run", "")

if not INSTALL_CMD or not CHECK_CMD or not SCREENSHOT_CMD:
    logging.error("Ошибка: отсутствуют команды для flameshot в config.json!")
    exit(1)


def check_flameshot_installed():
    """Проверяет, установлен ли flameshot"""
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


def install_flameshot():
    """Пытается установить flameshot, если его нет"""
    logging.warning("Flameshot не найден, выполняю установку...")
    try:
        subprocess.run(INSTALL_CMD, shell=True, check=True)
        logging.info("Flameshot успешно установлен.")
    except subprocess.CalledProcessError:
        logging.error("Ошибка установки flameshot! Установите его вручную.")


def take_screenshot():
    """Делает скриншот с flameshot и возвращает путь к файлу"""
    if not check_flameshot_installed():
        install_flameshot()
        if not check_flameshot_installed():
            logging.error("Flameshot не установлен. Скриншот не может быть создан.")
            return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(SESSION_DIR, f"screenshot_{timestamp}.png")

    try:
        # Формируем команду из конфига
        command = SCREENSHOT_CMD.replace("screenshot.png", screenshot_path)

        logging.info(f"Выполняю команду: {command}")
        subprocess.run(command, shell=True, check=True)
        subprocess.run("wtype Shift", shell=True, check=False)

        # Ожидание появления файла вместо `time.sleep(1)`
        start_time = time.time()
        while not os.path.exists(screenshot_path):
            if time.time() - start_time > 3:  # Ждем максимум 3 секунды
                logging.error(f"Файл не найден после скриншота: {screenshot_path}")
                return None
            time.sleep(0.1)

        logging.info(f"Скриншот сохранён: {screenshot_path}")
        return screenshot_path

    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка при создании скриншота: {e}")
        return None
