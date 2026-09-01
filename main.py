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
TOKEN = os.getenv("BOT_TOKEN", "8818268231:AAGuHw1NkORyeUn7h6iseVRISTr_ydWgRJI")

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

# Состояния FSM для регистрации/привязки ID
class RegistrationStates(StatesGroup):
    waiting_for_id = State()

# --- КЛАВИАТУРЫ ---
def get_register_keyboard() -> InlineKeyboardMarkup:
    """Главная клавиатура: Старт регистрации, Партнерка 1win и Поддержка"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Привязать ID / Начать", callback_data="start_registration")],
        [InlineKeyboardButton(text="💎 Играть / 1win", url="https://one-vv4866.com/?open=register&p=i390")],
        [InlineKeyboardButton(text="💬 Поддержка", url="https://t.me/Dexterslive")]
    ])

def get_mines_keyboard() -> InlineKeyboardMarkup:
    """Генерирует клавиатуру выбора мин (1, 3, 5, 7), кнопку 1win, меню и поддержку"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💣 1", callback_data="set_mines_1"),
            InlineKeyboardButton(text="💣 3", callback_data="set_mines_3"),
            InlineKeyboardButton(text="💣 5", callback_data="set_mines_5"),
            InlineKeyboardButton(text="💣 7", callback_data="set_mines_7"),
        ],
        [
            InlineKeyboardButton(text="💎 Играть на 1win", url="https://one-vv4866.com/?open=register&p=i390")
        ],
        [
            InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu"),
            InlineKeyboardButton(text="💬 Поддержка", url="https://t.me/Dexterslive")
        ]
    ])

# --- МАТЕМАТИКА И ВИЗУАЛ СИГНАЛОВ ---
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
    max_allowed_prob = 96.0
    min_allowed_prob = 60.0
    factor = (mines_count - 1) / (7 - 1)
    scaled_prob = max_allowed_prob - (max_allowed_prob - min_allowed_prob) * factor
    return int(round(scaled_prob))

def generate_mines_grid(mines_count: int) -> str:
    """Генерирует визуальное игровое поле 5x5 со случайными безопасными ячейками (⭐) и закрытыми (⬛)"""
    total_cells = 25
    safe_count = max(1, 5 - (mines_count // 2))
    
    cells = list(range(1, total_cells + 1))
    safe_spots = set(random.sample(cells, safe_count))
    
    grid_str = ""
    for r in range(5):
        row_chars = []
        for c in range(5):
            cell_num = r * 5 + c + 1
            if cell_num in safe_spots:
                row_chars.append("⭐")
            else:
                row_chars.append("⬛")
        grid_str += " ".join(row_chars) + "\n"
        
    return grid_str

# --- ОБРАБОТЧИКИ КОМАНД И КНОПОК ---
@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()  # Сбрасываем любые зависшие состояния принудительно
    text = (
        "🎮 **FastSignal | Аналитический терминал**\n\n"
        "⚡️ Синхронизируй ID с системой, лови точные сигналы раундов и забирай максимум профита в два клика!\n\n"
        "👉 Нажми кнопку ниже, чтобы начать процесс привязки ID."
    )
    await message.answer(text, reply_markup=get_register_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "start_registration")
async def start_reg_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(RegistrationStates.waiting_for_id)
    await callback.message.edit_text(
        "✍️ Отправь свой **ID** из профиля ответным сообщением:",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(RegistrationStates.waiting_for_id)
async def receive_user_id(message: types.Message, state: FSMContext):
    user_id_text = message.text.strip()
    await state.update_data(user_game_id=user_id_text)
    
    # Добавленный текст с бонусами сразу после привязки ID
    bonus_text = (
        f"✅ ID <code>{user_id_text}</code> успешно привязан!\n\n"
        "🎁 Кстати, за пополнение дают вкусные бонусы — можешь отыграть их в любом слоте!\n\n"
        "💣 Выбери количество мин для анализа раунда:"
    )
    
    await message.answer(
        bonus_text,
        reply_markup=get_mines_keyboard(),
        parse_mode="HTML"
    )
    await state.clear()

@router.callback_query(F.data.startswith("set_mines_"))
async def process_mines_selection(callback: types.CallbackQuery):
    mines_count = int(callback.data.split("_")[-1])
    
    current_mult = calculate_multiplier(mines_count, steps_opened=1)
    win_probability = calculate_win_probability(mines_count)
    visual_grid = generate_mines_grid(mines_count)
    
    text = (
        f"⚙️ **Анализ параметров:**\n"
        f"💣 Количество мин: **{mines_count}**\n"
        f"🎯 Вероятность успеха: **{win_probability}%**\n"
        f"📊 Ожидаемый коэффициент (Шаг 1): **{current_mult}x**\n\n"
        f"📍 **Сигнал (безопасные лунки):**\n"
        f"{visual_grid}\n"
        f"🔄 Выберите другое количество или перейдите к игре:"
    )
    
    try:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=get_mines_keyboard())
    except TelegramBadRequest:
        pass  # Игнорируем ошибку, если пользователь нажал ту же самую кнопку повторно
    await callback.answer()

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🎮 Главное меню аналитики. Выберите действие:",
        reply_markup=get_register_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

# --- СЕРВЕР ДЛЯ ПОДДЕРЖАНИЯ РАБОТЫ НА RENDER (aiohttp) ---
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
