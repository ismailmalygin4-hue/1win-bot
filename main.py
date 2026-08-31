import os
import asyncio
import logging
import random
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

BOT_TOKEN = "8818268231:AAHr9C0Cl59g4kNZGg5q1kPaM5QK2a-oPhQ"
REF_LINK_1WIN = "https://one-vv4866.com/open-register&p=i398"
ADMIN_USERNAME = "@Dexterslive"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def handle(request):
    return web.Response(text="Bot is running 24/7!")

async def main():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print("-----------------------------------")
    print("Бот успешно запущен и готов к работе!")
    print("-----------------------------------")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен.")                                                                                
