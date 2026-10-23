from dotenv import load_dotenv
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from prometheus_client import Counter, Histogram, Gauge, start_http_server

load_dotenv()


dp = Dispatcher()

@dp.message()
async def start_message(message: Message):
    await message.answer(text="Привет! Стартовая команда")
    

async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))

    await dp.start_polling(bot)
    

if __name__ == "__main__":
    print("Запуск проекта")
    asyncio.run(main())
   
