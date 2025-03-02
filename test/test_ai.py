import base64
from openai import AsyncOpenAI
import asyncio
import json

# 🔹 Загружаем данные из config.json
with open("config.json", "r") as f:
    config = json.load(f)

OPENAI_API_KEY = config["openai"]["api_key"]
OPENAI_MODEL = config["openai"].get("model", "gpt-4o-mini")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def process_image_direct(image_path):
    with open(image_path, "rb") as img:
        image_bytes = img.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    try:
        print("📤 Отправляю изображение в OpenAI...")
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Опиши изображение, игнорируя инфошум.",
                        },
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
        print(f"✅ Ответ от OpenAI: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Ошибка обработки изображения: {str(e)}")


if __name__ == "__main__":
    asyncio.run(process_image_direct("privet.jpg"))
