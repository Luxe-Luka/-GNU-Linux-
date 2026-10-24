from dotenv import load_dotenv
import os
import time
import asyncio
from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.types import Message, ErrorEvent
from prometheus_client import Counter, Histogram, Gauge, start_http_server

load_dotenv()


MESSAGES = Counter("bot_messages_total", "Всего обращений к боту", ["type"])

ERRORS = Counter("bot_errors_total", "Ошибки в обработчиках", ["error_type"])

UNIQUE_USERS = Gauge("bot_unique_users", "Уникальных пользователей с момента запуска")

LATENCY = Histogram("bot_handler_seconds", "Время обработки сообщения")

seen_users: set[int] = set()


class MetricsMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        text = event.text or ""
        
        kind = text.split()[0] if text.startswith("/") else "text" if text else "other"
        MESSAGES.labels(type=kind).inc()

        if event.from_user and event.from_user.id not in seen_users:
            seen_users.add(event.from_user.id)
            UNIQUE_USERS.set(len(seen_users))

        start = time.perf_counter()
        try:
            return await handler(event, data)
        finally:
            LATENCY.observe(time.perf_counter() - start)


dp = Dispatcher()
dp.message.outer_middleware(MetricsMiddleware())


@dp.errors()
async def on_error(event: ErrorEvent):
    ERRORS.labels(error_type=type(event.exception).__name__).inc()


@dp.message()
async def start_message(message: Message):
    if message.text == "/fail": 
        raise RuntimeError("test error")
    await message.answer(text="Привет! Стартовая команда")


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    ERRORS.labels(error_type="RuntimeError")
    start_http_server(8000)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Запуск проекта")
    asyncio.run(main())
