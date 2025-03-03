import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from src.ai_api import process_image
from src.config_handler import ConfigHandler

# Установка языка 1 раз при старте
ConfigHandler.update_language()


# Функция перевода строк
def translate(text):
    return ConfigHandler.translate(text)


# Инициализация бота и диспетчера
bot = Bot(token=ConfigHandler.get_value("telegram.bot_token"))
dp = Dispatcher()


# Обработчик /start
@dp.message(Command("start"))
async def handle_start(message: types.Message):
    chat_id = message.chat.id
    saved_chat_id = ConfigHandler.get_value("telegram.chat_id", 0)

    if saved_chat_id not in [None, 0]:
        logging.info(f"chat_id уже сохранен: {saved_chat_id}")
        await message.answer(translate("Бот уже активирован."))
        return

    ConfigHandler.save_value("telegram.chat_id", chat_id)
    logging.info(f"chat_id {chat_id} {translate('автоматически сохранен.')}")
    await message.answer(
        translate("Привет! Отправь мне изображение, и я его обработаю.")
    )


# Обработка изображений
async def process_received_file(file_id, chat_id):
    try:
        file_info = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{ConfigHandler.get_value('telegram.bot_token')}/{file_info.file_path}"

        with requests.Session() as session:
            img_data = session.get(file_url).content

        received_image_path = "logs/received.png"
        with open(received_image_path, "wb") as handler:
            handler.write(img_data)
        logging.info(f"{translate('Файл сохранен:')} {received_image_path}")

        await bot.send_message(
            chat_id, translate("Изображение загружено. Обрабатываю через ИИ...")
        )
        response = await process_image(received_image_path)
        await bot.send_message(chat_id, response)
        logging.info(translate("Обработка завершена."))
    except Exception as e:
        logging.error(f"{translate('Ошибка обработки изображения:')} {e}")
        await bot.send_message(chat_id, translate(f"Ошибка обработки изображения: {e}"))


# Обработчик медиа
@dp.message(lambda message: message.photo or message.document)
async def handle_media(message: types.Message):
    chat_id = message.chat.id
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    await process_received_file(file_id, chat_id)


# Основной запуск бота
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
