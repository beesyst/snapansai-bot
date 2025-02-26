import base64
from openai import AsyncOpenAI
import json

# 🔹 Загружаем конфиг
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# 🔧 Строго берём данные из конфига
try:
    OPENAI_API_KEY = config["openai"]["api_key"]
    OPENAI_MODEL = config["openai"]["model"]
    PROMPT = config["openai"]["prompt"]
except KeyError as e:
    raise ValueError(f"❌ Ошибка: отсутствует параметр в config.json: {e}")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def process_image(image_path):
    with open(image_path, "rb") as img:
        image_bytes = img.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    try:
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
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Ошибка обработки изображения: {str(e)}"
