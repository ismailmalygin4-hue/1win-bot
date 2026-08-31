import os
import asyncio
import logging
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Ваш токен бота
BOT_TOKEN = "8818268231:AAGbMU8_r40HRmB5773kS9dGK2e1yjR4h1g"
REF_LINK_1WIN = "https://one-vv4866.com/open-register&p=i398"
ADMIN_USERNAME = "@Dexterslive"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Зарегистрироваться", url=REF_LINK_1WIN)],
            [InlineKeyboardButton(text="Поддержка", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")]
        ]
    )
    await message.answer("Добро пожаловать! Нажмите кнопку ниже для перехода:", reply_markup=keyboard)

async def handle(request):
    return web.Response(text="Bot is running 24/7!")

# Функция-пингер: сама себя будит каждые 5 минут
async def self_ping():
    # Получаем URL нашего приложения из переменных окружения Render или вставляем вручную
    # (Render автоматически задает PORT, а адрес сайта можно прописать или оставить заглушку)
    await asyncio.sleep(10) # ждем пока сервер запустится
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    
    if not render_url:
        print("Внимание: RENDER_EXTERNAL_URL не найден, пингер отключен (но бот работает).")
        return

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(render_url) as response:
                    print(f"Пингер сработал! Статус: {response.status}")
            except Exception as e:
                print(f"Ошибка пингера: {e}")
            # Повторяем каждые 5 минут (300 секунд)
            await asyncio.sleep(300)

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

    # Запускаем встроенный пингер в фоновом режиме
    asyncio.create_task(self_ping())

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен.")
