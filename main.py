import os
import asyncio
import logging
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# 1. Ваши настройки
BOT_TOKEN = "8818268231:AAGbMU8_r40HRmB5773kS9dGK2e1yjR4h1g"
REF_LINK_1WIN = "https://one-vv4866.com/open-register&p=i398"
ADMIN_USERNAME = "signalssupport1WIN"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Состояния для пошаговой регистрации (ввода ID)
class RegistrationStates(StatesGroup):
    waiting_for_id = State()

# Клавиатура с ссылкой на 1win и кнопкой отправки ID
def get_register_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Зарегистрироваться на 1win", url=REF_LINK_1WIN)],
            [InlineKeyboardButton(text="✅ Я зарегистрировался, отправить ID", callback_data="send_id_step")]
        ]
    )

# Главное меню, которое появляется после успешной привязки ID
def get_main_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Получить сигнал", callback_data="get_signal")],
            [InlineKeyboardButton(text="💬 Поддержка", url=f"https://t.me/{ADMIN_USERNAME}")]
        ]
    )

@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        "👋 Привет!\n\n"
        "Чтобы получать сигналы, нужно выполнить 2 простых шага:\n"
        "1. Зарегистрироваться по ссылке ниже.\n"
        "2. Скопировать **ID** из своего профиля 1win и прислать его сюда.\n\n"
        "Нажмите кнопку «Зарегистрироваться», если еще не сделали этого:"
    )
    await message.answer(text, reply_markup=get_register_keyboard(), parse_mode="Markdown")

# Обработка нажатия на кнопку "Я зарегистрировался"
@dp.callback_query(F.data == "send_id_step")
async def process_send_id_button(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Отлично! Теперь зайдите в личный кабинет 1win, скопируйте свой **ID** (цифры) и отправьте его сюда ответным сообщением:",
        parse_mode="Markdown"
    )
    await state.set_state(RegistrationStates.waiting_for_id)
    await callback.answer()

# Ловим ID, который пользователь отправляет текстом
@dp.message(RegistrationStates.waiting_for_id)
async def receive_user_id(message: types.Message, state: FSMContext):
    user_id_text = message.text.strip()
    
    # Здесь можно добавить проверку, что пользователь прислал цифры (опционально)
    # Сохраняем ID (пока просто выводим в консоль сервера, позже можно записывать в базу данных)
    print(let := f"Получен ID от пользователя {message.from_user.id}: {user_id_text}")
    
    await state.clear()
    
    await message.answer(
        f"✅ **ID успешно сохранен!** (Ваш ID: `{user_id_text}`)\n\n"
        "Теперь вам доступны сигналы. Нажмите кнопку ниже:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )

# Заглушка для будущих сигналов
@dp.callback_query(F.data == "get_signal")
async def send_signal_handler(callback: types.CallbackQuery):
    await callback.message.answer("🎲 Сигнал: **Меньше / Больше** — Ждите обновления следующего раунда!", parse_mode="Markdown")
    await callback.answer()

async def handle(request):
    return web.Response(text="Bot is running 24/7!")

# Встроенный пингер, чтобы сервер не засыпал
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
