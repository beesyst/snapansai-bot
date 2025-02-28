import base64
import json
import logging
from openai import AsyncOpenAI

# Настройка логирования
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Пути к файлам конфигурации
CONFIG_FILE = "config.json"
LANG_FILE = "lang.json"


# Загрузка конфигурации
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"❌ Файл {path} не найден.")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"❌ Ошибка разбора {path}: {e}")
        raise


config = load_json(CONFIG_FILE)
lang_data = load_json(LANG_FILE)

# Получаем язык из config.json, если его нет — крашим
if "language" not in config or config["language"] not in lang_data:
    error_msg = "❌ Ошибка: язык не указан в config.json или отсутствует в lang.json"
    logging.error(error_msg)
    raise ValueError(error_msg)

LANG_SETTING = config["language"]

# Берем промпт из lang.json на нужном языке
PROMPT = lang_data[LANG_SETTING]["prompt"]

# Проверка API-ключей
try:
    OPENAI_API_KEY = config["openai"]["api_key"]
    OPENAI_MODEL = config["openai"]["model"]
except KeyError as e:
    error_msg = f"❌ Ошибка: отсутствует параметр в config.json: {e}"
    logging.error(error_msg)
    raise ValueError(error_msg)

# Инициализация OpenAI клиента
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


# Функция обработки изображения через OpenAI
async def process_image(image_path):
    try:
        with open(image_path, "rb") as img:
            image_bytes = img.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        logging.info(f"Начинаю обработку изображения: {image_path}")

        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": PROMPT,
                        },  # Используем локализованный промпт
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )

        result = response.choices[0].message.content

        # Убираем всё форматирование и отправляем только чистый текст
        plain_result = result.replace("*", "").replace("_", "").replace("`", "")

        logging.info("Изображение успешно обработано.")
        return plain_result

    except Exception as e:
        error_msg = f"❌ Ошибка обработки изображения: {str(e)}"
        logging.error(error_msg)
        return error_msg
