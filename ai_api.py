import base64
import json
import logging
from openai import AsyncOpenAI

# 🔹 Настройка логирования
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 🔹 Загрузка конфигурации
def load_config(path="config.json"):
    try:
        with open(path, "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.error("❌ Файл config.json не найден.")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"❌ Ошибка разбора config.json: {e}")
        raise

config = load_config()

# 🔧 Проверка обязательных параметров
try:
    OPENAI_API_KEY = config["openai"]["api_key"]
    OPENAI_MODEL = config["openai"]["model"]
    PROMPT = config["openai"]["prompt"]
except KeyError as e:
    error_msg = f"❌ Ошибка: отсутствует параметр в config.json: {e}"
    logging.error(error_msg)
    raise ValueError(error_msg)

# 🔹 Инициализация клиента OpenAI
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# 🔹 Обработка изображения
async def process_image(image_path):
    try:
        with open(image_path, "rb") as img:
            image_bytes = img.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        logging.info(f"🖼️ Начинаю обработку изображения: {image_path}")

        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
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
        logging.info("✅ Изображение успешно обработано.")
        return result

    except Exception as e:
        error_msg = f"❌ Ошибка обработки изображения: {str(e)}"
        logging.error(error_msg)
        return error_msg
