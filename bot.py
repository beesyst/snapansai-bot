import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from ai_api import process_image
import json
import requests
import os

# 🔹 Загрузка конфигурации из config.json
CONFIG_PATH = "config.json"


def load_config():
    with open(CONFIG_PATH, "r") as file:
        return json.load(file)


def save_config(config):
    with open(CONFIG_PATH, "w") as file:
        json.dump(config, file, indent=4)
    logging.info("✅ chat_id успешно сохранен в config.json!")


config = load_config()
TELEGRAM_TOKEN = config["telegram"]["bot_token"]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


# 🔧 Универсальная обработка изображений (photo или document)
async def process_received_file(file_id, chat_id):
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
    logging.info(f"🌐 Ссылка на изображение: {file_url}")

    img_data = requests.get(file_url).content
    with open("received.png", "wb") as handler:
        handler.write(img_data)

    await bot.send_message(
        chat_id, "🖼️ Изображение загружено. Обрабатываю через OpenAI..."
    )
    response = await process_image("received.png")
    await bot.send_message(chat_id, f"🤖 Ответ ИИ:\n{response}")


@dp.message(F.text == "/start")
async def handle_start(message: Message):
    chat_id = message.chat.id
    config = load_config()
    if config["telegram"].get("chat_id") != chat_id:
        config["telegram"]["chat_id"] = chat_id
        save_config(config)
        logging.info(f"✅ chat_id {chat_id} автоматически сохранен!")
    await message.answer("👋 Привет! Отправь мне изображение, и я его обработаю.")


@dp.message(F.photo | F.document)
async def handle_media(message: Message):
    chat_id = message.chat.id

    # ✅ Проверяем: изображение в photo или document
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer("⚠️ Я не смог определить тип файла.")
        return

    logging.info(f"📝 Получен file_id: {file_id}")
    await process_received_file(file_id, chat_id)


@dp.message(F.text)
async def echo_message(message: Message):
    await message.answer("📩 Отправь изображение, чтобы я его обработал!")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
