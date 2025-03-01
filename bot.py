import asyncio
import logging
import json
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from ai_api import process_image

# Логирование в bot.log
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# Конфиг-менеджер
class ConfigHandler:
    CONFIG_PATH = "config.json"
    LANG_PATH = "lang.json"

    @classmethod
    def load_config(cls):
        with open(cls.CONFIG_PATH, "r") as file:
            return json.load(file)

    @classmethod
    def save_config(cls, config):
        with open(cls.CONFIG_PATH, "w") as file:
            json.dump(config, file, indent=4)
        logging.info("chat_id успешно сохранен в config.json.")

    @classmethod
    def load_language(cls):
        with open(cls.LANG_PATH, "r") as file:
            return json.load(file)


config = ConfigHandler.load_config()
lang_data = ConfigHandler.load_language()
LANG_SETTING = config["language"]


# Функция перевода строк
def translate(text):
    return lang_data.get(LANG_SETTING, {}).get(text, text)


bot = Bot(token=config["telegram"]["bot_token"])
dp = Dispatcher()


# Обработка изображения
async def process_received_file(file_id, chat_id):
    try:
        file_info = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{config['telegram']['bot_token']}/{file_info.file_path}"

        with requests.Session() as session:
            img_data = session.get(file_url).content

        with open("received.png", "wb") as handler:
            handler.write(img_data)
        logging.info(translate("Файл сохранен: received.png"))

        await bot.send_message(
            chat_id, translate("Изображение загружено. Обрабатываю через ИИ...")
        )
        response = await process_image("received.png")
        await bot.send_message(chat_id, response)
        logging.info(translate("Обработка завершена."))
    except Exception as e:
        logging.error(translate(f"Ошибка обработки изображения: {e}"))
        await bot.send_message(chat_id, translate(f"Ошибка обработки изображения: {e}"))


# Обработка /start
@dp.message(F.text == "/start")
async def handle_start(message: Message):
    chat_id = message.chat.id
    if config["telegram"].get("chat_id") != chat_id:
        config["telegram"]["chat_id"] = chat_id
        ConfigHandler.save_config(config)
        logging.info(f"chat_id {chat_id} {translate('автоматически сохранен.')}")

    await message.answer(
        translate("Привет! Отправь мне изображение, и я его обработаю.")
    )


# Обработка медиа
@dp.message(F.photo | F.document)
async def handle_media(message: Message):
    chat_id = message.chat.id
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    await process_received_file(file_id, chat_id)


# Основной запуск бота
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
