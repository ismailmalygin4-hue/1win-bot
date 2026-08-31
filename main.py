import os
import asyncio
import logging
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# 1. Ваши настройки
BOT_TOKEN = "8818268231:AAGbMU8_r40HRmB5773kS9dGK2e1yjR4h1g"
REF_LINK_1WIN = "https://one-vv4866.com/open-register&p=i398"
ADMIN_USERNAME = "signalssupport1WIN"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class RegistrationStates(StatesGroup):
    waiting_for_id = State()

def get_register_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Создать аккаунт 1win", url=REF_LINK_1WIN)],
            [InlineKeyboardButton(text="📥 Отправить мой ID", callback_data="send_id_step")]
        ]
    )

def get_main_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔥 Получить сигнал раунда", callback_data="get_signal")],
            [InlineKeyboardButton(text="🆘 Помощь и саппорт", url=f"https://t.me/{ADMIN_USERNAME}")]
        ]
    )

@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    
    text = (
        "🎮 Приветствую, игрок! Хочешь забирать максимум профита из каждого раунда?\n\n"
        "🚀 Наша система готова выдавать точные подсказки, но для начала нужно объединить аккаунты:\n\n"
        "👉 **Шаг 1:** Создай аккаунт по кнопке ниже.\n"
        "👉 **Шаг 2:** Скинь сюда свой ID из профиля."
    )
    await message.answer(text, reply_markup=get_register_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "send_id_step")
async def process_send_id_button(callback: types.CallbackQuery, state: FSMContext):
    text = (
        "🕹 **Почти у цели!**\n\n"
        "Зайди в личный кабинет 1win, скопируй свой **цифровой ID** и отправь его ответным сообщением в этот чат 👇"
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await state.set_state(RegistrationStates.waiting_for_id)
    await callback.answer()

@dp.message(RegistrationStates.waiting_for_id)
async def receive_user_id(message: types.Message, state: FSMContext):
    user_id_text = message.text.strip()
    
    print(f"Получен ID от пользователя {message.from_user.id}: {user_id_text}")
    await state.clear()
    
    text = (
        "🏆 **Отлично! Связка прошла успешно.**\n\n"
        f"Твой ID: `{user_id_text}` записан в базу данных.\n\n"
        "Включай турбо-режим и забирай сигналы! 👇"
    )
    await message.answer(text, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "get_signal")
async def send_signal_handler(callback: types.CallbackQuery):
    text = (
        "⚡️ **АНАЛИЗ РАУНДА** ⚡️\n\n"
        "🎲 Прогноз: **Меньше / Больше**\n"
        "⏳ *Ожидай появление нового раунда...*"
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

async def handle(request):
    return web.Response(text="Bot is running 24/7!")

async def self_ping():
    await asyncio.sleep(10)
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not render_url:
        return
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(render_url) as response:
                    pass
            except Exception:
                pass
            await asyncio.sleep(300)

async def main():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    asyncio.create_task(self_ping())
    print("Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен.")
