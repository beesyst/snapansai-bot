import json
import logging

# Настройка логирования
logging.basicConfig(
    filename="logs/bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class ConfigHandler:
    CONFIG_PATH = "config/config.json"
    LANG_PATH = "config/lang.json"
    _config = None
    _lang_data = None
    _language = "en"

    @classmethod
    def save_value(cls, path, value):
        """Сохраняет значение в config.json"""
        cls.load_config()

        keys = path.split(".")
        config_ref = cls._config

        for key in keys[:-1]:
            if key not in config_ref or not isinstance(config_ref[key], dict):
                config_ref[key] = {}
            config_ref = config_ref[key]

        config_ref[keys[-1]] = value

        try:
            with open(cls.CONFIG_PATH, "w", encoding="utf-8") as file:
                json.dump(cls._config, file, indent=2, ensure_ascii=False)
            logging.info(f"Значение {path} обновлено в config.json: {value}")
        except Exception as e:
            logging.error(f"Ошибка сохранения config.json: {e}")

    @classmethod
    def load_config(cls):
        """Загружает конфиг в память 1 раз"""
        if cls._config is None:
            try:
                with open(cls.CONFIG_PATH, "r", encoding="utf-8") as file:
                    cls._config = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                cls._config = {}
        return cls._config

    @classmethod
    def load_language(cls):
        """Загружает языковой файл в память 1 раз"""
        if cls._lang_data is None:
            try:
                with open(cls.LANG_PATH, "r", encoding="utf-8") as file:
                    cls._lang_data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                cls._lang_data = {}
        return cls._lang_data

    @classmethod
    def update_language(cls):
        """Устанавливает язык 1 раз при старте"""
        cls.load_config()
        cls._language = cls._config.get("language", "en")
        cls.load_language()

    @classmethod
    def translate(cls, text):
        """Переводит строку на указанный язык"""
        return cls._lang_data.get(cls._language, {}).get(text, text)

    @classmethod
    def get_value(cls, path, default=None):
        """Читает значение из конфига без лишних логов"""
        cls.load_config()
        keys = path.split(".")
        value = cls._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    @classmethod
    def check_api_key(cls, strict=False):
        """Проверяет, есть ли API-ключ для AI.

        - strict=True: Вызывает ошибку, если ключ отсутствует.
        - strict=False: Просто логирует инфо и отключает AI.
        """
        openai_key = cls.get_value("openai.api_key", "")
        deepseek_key = cls.get_value("deepseek.api_key", "")

        if not openai_key and not deepseek_key:
            if strict:
                raise ValueError("Ошибка: отсутствует параметр API в config.json")
            else:
                logging.info("API-ключ отсутствует. Функционал AI временно отключен.")
                return False
        return True
