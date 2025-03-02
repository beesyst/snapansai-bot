import base64
import asyncio
from openai import AsyncOpenAI
from src.config_handler import ConfigHandler
import logging


# Функция перевода строк
def translate(text):
    return ConfigHandler.translate(text)


# Промпт из lang.json на нужном языке
ConfigHandler.update_language()
PROMPT = ConfigHandler.translate("prompt")


# Функция обработки изображения через ИИ
async def process_image(image_path):
    openai_key = ConfigHandler.get_value("openai.api_key")
    openai_model = ConfigHandler.get_value("openai.model")

    if not openai_key or not openai_model:
        logging.error("Ошибка: отсутствует API-ключ. AI-функционал недоступен.")
        return translate("Ошибка: API-ключ отсутствует. Проверь config.json.")

    client = AsyncOpenAI(api_key=openai_key)

    max_retries = 3
    attempt = 0

    while attempt < max_retries:
        try:
            with open(image_path, "rb") as img:
                image_bytes = img.read()
            base64_image = base64.b64encode(image_bytes).decode("utf-8")

            logging.info(f"{translate('Начинаю обработку изображения')}: {image_path}")

            response = await client.chat.completions.create(
                model=openai_model,
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
            plain_result = result.replace("*", "").replace("_", "").replace("`", "")

            logging.info(translate("Изображение успешно обработано"))
            return plain_result

        except ConnectionResetError as e:
            attempt += 1
            logging.error(
                f"{translate('Ошибка обработки изображения')}: {e}. Повторная попытка ({attempt}/{max_retries})..."
            )
            await asyncio.sleep(3)

        except Exception as e:
            logging.error(f"{translate('Ошибка обработки изображения')}: {e}")
            return f"{translate('Ошибка обработки изображения')}: {e}"

    return f"{translate('Ошибка обработки изображения')}: {translate('Повторные попытки не помогли')}"
