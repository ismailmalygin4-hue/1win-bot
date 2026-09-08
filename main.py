import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web

# Токен твоего бота (убедись, что здесь твой актуальный токен)
TOKEN = os.getenv("BOT_TOKEN", "8818268231:AAEP8QDZXr2-8uVAdVWbIuLDDPzG72ZORhY")

# Ссылка на твое веб-приложение. 
# Если запускаешь локально для теста, обычно используют ngrok. 
# На хостинге (Render, Railway) сюда подставится адрес твоего сайта.
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://1win-bot-1.onrender.com")

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

class RegistrationStates(StatesGroup):
    waiting_for_id = State()

def get_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Запустить Мини-Приложение (Сигналы)", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="🌐 Зарегистрироваться на 1WIN", url="https://one-vv8000.com/?open=register&p=i390")],
        [InlineKeyboardButton(text="✍️ Прислать ID", callback_data="start_registration")],
        [InlineKeyboardButton(text="💬 Поддержка", callback_data="show_support")]
    ])

@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        "🎮 **FastSignal | Web App Terminal**\n\n"
        "⚡️ Нажми на кнопку ниже, чтобы открыть интерактивное приложение с сигналами прямо в Telegram!"
    )
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "start_registration")
async def start_reg_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(RegistrationStates.waiting_for_id)
    await callback.message.answer("✍️ Отправь свой **ID** из профиля 1WIN ответным сообщением:", parse_mode="Markdown")
    await callback.answer()

@router.message(RegistrationStates.waiting_for_id)
async def receive_user_id(message: types.Message, state: FSMContext):
    user_id_text = message.text.strip()
    await message.answer(
        f"✅ ID <code>{user_id_text}</code> успешно привязан!\n\n"
        "Теперь можешь запускать Mini App.",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    await state.clear()

@router.callback_query(F.data == "show_support")
async def show_support_handler(callback: types.CallbackQuery):
    support_text = "💬 Поддержка: пишите администратору <a href='https://t.me/Dexterslive'>@Dexterslive</a>"
    await callback.message.answer(support_text, parse_mode="HTML")
    await callback.answer()

# --- HTTP СЕРВЕР ДЛЯ РАЗДАЧИ index.html ---
async def handle_index(request):
    filename = "index.html"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        return web.Response(text=content, content_type="text/html")
    return web.Response(text="index.html not found in folder", status=404)

async def handle_ping(request):
    return web.Response(text="Web App Server is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_get("/ping", handle_ping)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    dp.include_router(router)
    await asyncio.gather(
        web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
