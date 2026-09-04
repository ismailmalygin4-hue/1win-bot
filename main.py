import asyncio
import logging
import os
import random
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
from aiohttp import web

# Токен вашего бота
TOKEN = os.getenv("BOT_TOKEN", "8818268231:AAH6nwla5aNaNv17x4S4hhzOvQwa27lAq7s")

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

class RegistrationStates(StatesGroup):
    waiting_for_id = State()

def get_register_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Зарегистрироваться на сайте 1WIN", url="https://one-vv8000.com/?open=register&p=i390")],
        [InlineKeyboardButton(text="🚀 Прислать ID (обязательно)", callback_data="start_registration")],
        [InlineKeyboardButton(text="💬 Поддержка", callback_data="show_support")]
    ])

def get_mines_keyboard(mines_count: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💣 1", callback_data="set_mines_1"),
            InlineKeyboardButton(text="💣 3", callback_data="set_mines_3"),
            InlineKeyboardButton(text="💣 5", callback_data="set_mines_5"),
            InlineKeyboardButton(text="💣 7", callback_data="set_mines_7"),
        ],
        [
            InlineKeyboardButton(text="🔴 Выдать сигнал", callback_data=f"get_signal_{mines_count}")
        ],
        [
            InlineKeyboardButton(text="💎 Играть на 1win", url="https://one-vv8000.com/?open=register&p=i390")
        ],
        [
            InlineKeyboardButton(text="◀️ Главное меню", callback_data="back_to_menu"),
            InlineKeyboardButton(text="💬 Поддержка", callback_data="show_support")
        ]
    ])

def calculate_multiplier(mines_count: int, steps_opened: int = 1) -> float:
    total_cells = 25
    safe_cells = total_cells - mines_count
    if steps_opened > safe_cells or steps_opened <= 0:
        return 1.0
    probability = 1.0
    for i in range(steps_opened):
        probability *= (safe_cells - i) / (total_cells - i)
    raw_multiplier = 1.0 / probability
    house_edge = 0.97
    return round(max(1.01, raw_multiplier * house_edge), 2)

def calculate_win_probability(mines_count: int) -> int:
    return int(round(95 - (mines_count * 1.5)))

def get_target_stars_count(mines_count: int) -> int:
    if mines_count == 1:
        return random.randint(4, 7)
    elif mines_count == 3:
        return random.randint(3, 5)
    elif mines_count == 5:
        return random.randint(2, 4)
    elif mines_count == 7:
        return random.randint(1, 2)
    return 2

def generate_grid_state(total_cells: int = 25, active_spots: set = None) -> str:
    if active_spots is None:
        active_spots = set()
    grid_str = ""
    for r in range(5):
        row_chars = []
        for c in range(5):
            cell_num = r * 5 + c + 1
            if cell_num in active_spots:
                row_chars.append("⭐")
            else:
                row_chars.append("🟦")
        grid_str += "".join(row_chars) + "\n"
    return grid_str

@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        "🎮 **Сигналы для mines (мины) 🎯**\n\n"
        "⚡️ Сначала пройдите регистрацию на сайте 1WIN по кнопке ниже, затем отправьте свой ID для доступа к сигналам!\n\n"
        "👉 Выберите нужное действие:"
    )
    await message.answer(text, reply_markup=get_register_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "start_registration")
async def start_reg_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(RegistrationStates.waiting_for_id)
    await callback.message.edit_text(
        "✍️ Отправь свой **ID** из профиля 1WIN ответным сообщением:",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(RegistrationStates.waiting_for_id)
async def receive_user_id(message: types.Message, state: FSMContext):
    user_id_text = message.text.strip()
    await state.update_data(user_game_id=user_id_text)
    
    bonus_text = (
        f"✅ ID <code>{user_id_text}</code> успешно привязан!\n\n"
        "🎁 Данные синхронизированы с сервером. Выберите режим анализа (количество мин):"
    )
    
    await message.answer(
        bonus_text,
        reply_markup=get_mines_keyboard(mines_count=3),
        parse_mode="HTML"
    )
    await state.clear()

@router.callback_query(F.data.startswith("set_mines_"))
async def process_mines_selection(callback: types.CallbackQuery):
    mines_count = int(callback.data.split("_")[-1])
    
    text = (
        f"🟢 **Сигналы для mines (мины) 🎯**\n\n"
        f"💣 Выбрано мин: **{mines_count}**\n\n"
        f"{generate_grid_state(25, set())}\n"
        f"👇 Нажмите кнопку ниже для получения сигнала:"
    )
    
    try:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=get_mines_keyboard(mines_count))
    except TelegramBadRequest:
        pass  
    await callback.answer()

# --- АНИМАЦИЯ ВЫДАЧИ СИГНАЛА КАК НА ВИДЕО ---
@router.callback_query(F.data.startswith("get_signal_"))
async def process_get_signal(callback: types.CallbackQuery):
    mines_count = int(callback.data.split("_")[-1])
    win_prob = calculate_win_probability(mines_count)
    current_mult = calculate_multiplier(mines_count, steps_opened=1)
    
    # 1. Шаг: Очищаем поле и запускаем процесс сканирования
    try:
        await callback.message.edit_text(
            f"🟢 **Сигналы для mines (мины) 🎯**\n\n"
            f"🔍 **Анализ ячеек...** (Мин: {mines_count})\n\n"
            f"{generate_grid_state(25, set())}",
            parse_mode="Markdown"
        )
    except TelegramBadRequest:
        pass

    await asyncio.sleep(0.5)

    # Генерация позиций звезд по твоим правилам
    total_cells = 25
    target_count = get_target_stars_count(mines_count)
    cells = list(range(1, total_cells + 1))
    random.seed(os.urandom(4))
    final_spots = random.sample(cells, target_count)

    # 2. Шаг: Плавное зажжение звезд по одной (анимация как на видео)
    currently_shown = set()
    for spot in final_spots:
        currently_shown.add(spot)
        try:
            await callback.message.edit_text(
                f"🟢 **Сигналы для mines (мины) 🎯**\n\n"
                f"⚡️ **Генерация сигнала...**\n\n"
                f"{generate_grid_state(25, currently_shown)}",
                parse_mode="Markdown"
            )
        except TelegramBadRequest:
            pass
        await asyncio.sleep(0.35)  # Скорость появления каждой звезды

    # 3. Шаг: Финальный экран сигнала с кнопкой управления
    final_text = (
        f"🟢 **Сигналы для mines (мины) 🎯**\n\n"
        f"{generate_grid_state(25, final_spots)}"
    )

    try:
        await callback.message.edit_text(
            final_text, 
            parse_mode="Markdown", 
            reply_markup=get_mines_keyboard(mines_count)
        )
    except TelegramBadRequest:
        pass
        
    await callback.answer("✅ Сигнал выдан!")

@router.callback_query(F.data == "show_support")
async def show_support_handler(callback: types.CallbackQuery):
    support_text = (
        "💬 <b>Центр поддержки</b>\n\n"
        "Возникли вопросы по работе бота или привязке ID? "
        "Свяжитесь с нашей службой поддержки!\n\n"
        "👉 Напишите администратору: <a href='https://t.me/Dexterslive'>@Dexterslive</a>"
    )
    support_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
    await callback.message.edit_text(support_text, parse_mode="HTML", reply_markup=support_keyboard)
    await callback.answer()

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🎮 **Сигналы для mines (мины) 🎯**\n\n"
        "⚡️ Сначала пройдите регистрацию на сайте 1WIN по кнопке ниже, затем отправьте свой ID для доступа к сигналам!\n\n"
        "👉 Выберите нужное действие:",
        reply_markup=get_register_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
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
