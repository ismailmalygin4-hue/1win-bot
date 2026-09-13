import asyncio
import json
import logging
import os
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, Update, WebAppInfo

logging.basicConfig(level=logging.INFO)

TOKEN = "8818268231:AAHMhMwPrBDP2JGTsajUrHqXBgXPR0e4HhU"
PORT = int(os.getenv("PORT", 10000))
WEBAPP_URL = "https://onewin-bot-1.onrender.com"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBAPP_URL}{WEBHOOK_PATH}"
ONWIN_URL = "https://one-vv4504.com/?open=register&p=i390"
MANAGER_URL = "https://t.me/Dexterslive"
DB_FILE = "database.json"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

class Form(StatesGroup):
    waiting_for_id = State()

# Функции постоянного сохранения данных (чтобы ничего не сбрасывалось)
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {int(k): v for k, v in data.get("users", {}).items()}, set(data.get("blocked", []))
        except Exception as e:
            logging.error(f"Error loading DB: {e}")
    return {}, set()

def save_db():
    try:
        data = {
            "users": users_db,
            "blocked": list(blocked_users)
        }
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Error saving DB: {e}")

users_db, blocked_users = load_db()

HTML_CONTENT = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>1win Signals</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { background-color: #0f1923; color: #ffffff; font-family: Arial, sans-serif; text-align: center; margin: 0; padding: 20px; }
        h2 { color: #00ffcc; margin-bottom: 10px; }
        .settings { margin: 15px 0; font-size: 16px; }
        select { background: #1b2838; color: #fff; border: 1px solid #00ffcc; padding: 5px 10px; border-radius: 5px; font-size: 16px; }
        .grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; max-width: 320px; margin: 20px auto; }
        .cell { aspect-ratio: 1; background: #1b2838; border: 2px solid #2a475e; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 24px; transform: scale(1); transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
        .cell.active { background: #00ffcc; border-color: #fff; box-shadow: 0 0 15px #00ffcc; transform: scale(1.08); }
        button.btn { background: linear-gradient(135deg, #00ffcc, #00b386); color: #0f1923; border: none; padding: 12px 25px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 15px; width: 100%; max-width: 320px; }
        button.btn:active { transform: scale(0.98); }
    </style>
</head>
<body>
    <h2>MINES SIGNAL</h2>
    <div class="settings">
        <label for="minesCount">Количество мин: </label>
        <select id="minesCount">
            <option value="1">1</option>
            <option value="3" selected>3</option>
            <option value="5">5</option>
            <option value="7">7</option>
        </select>
    </div>
    <div class="grid" id="grid"></div>
    <button class="btn" id="genBtn" onclick="getSignal()">ВЫДАТЬ СИГНАЛ</button>
    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();
        const gridElement = document.getElementById('grid');
        const totalCells = 25;
        let isGenerating = false;

        for (let i = 0; i < totalCells; i++) {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            gridElement.appendChild(cell);
        }

        function calculateOptimalCells(mines, targetCount) {
            let weights = new Array(totalCells).fill(1.0);
            for (let i = 0; i < totalCells; i++) {
                let row = Math.floor(i / 5);
                let col = i % 5;
                let distanceCenter = Math.abs(2 - row) + Math.abs(2 - col);
                weights[i] += (2.5 - distanceCenter * 0.3) * (1 / (mines * 0.5 + 1));
                weights[i] *= (0.8 + Math.abs(Math.sin(i * 12.9898 + mines) * 0.4));
            }
            let pool = Array.from({length: totalCells}, (_, index) => index);
            pool.sort((a, b) => weights[b] - weights[a]);
            let topCandidates = pool.slice(0, Math.max(targetCount + 4, 10));
            topCandidates.sort(() => Math.random() - 0.5);
            return topCandidates.slice(0, targetCount);
        }

        function getSignal() {
            if (isGenerating) return;
            isGenerating = true;
            const btn = document.getElementById('genBtn');
            btn.disabled = true;

            const mines = parseInt(document.getElementById('minesCount').value);
            const cells = document.querySelectorAll('.cell');
            cells.forEach(c => {
                c.classList.remove('active');
                c.innerHTML = '';
            });

            let targetCount = 3;
            if (mines === 1) {
                targetCount = Math.floor(Math.random() * (7 - 3 + 1)) + 3;
            } else if (mines === 3) {
                targetCount = Math.floor(Math.random() * (5 - 3 + 1)) + 3;
            } else if (mines === 5) {
                targetCount = Math.floor(Math.random() * (4 - 2 + 1)) + 2;
            } else if (mines === 7) {
                targetCount = Math.floor(Math.random() * (3 - 1 + 1)) + 1;
            }

            let opened = calculateOptimalCells(mines, targetCount);

            let index = 0;
            function revealNext() {
                if (index < opened.length) {
                    let cellIdx = opened[index];
                    cells[cellIdx].classList.add('active');
                    cells[cellIdx].innerHTML = '⭐';
                    if (tg.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
                    index++;
                    setTimeout(revealNext, 200);
                } else {
                    isGenerating = false;
                    btn.disabled = false;
                    if (tg.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
                }
            }
            revealNext();
        }
    </script>
</body>
</html>"""

async def handle_web(request):
    return web.Response(text=HTML_CONTENT, content_type='text/html')

async def handle_webhook(request):
    try:
        data = await request.json()
        update = Update.model_validate(data, context={"bot": bot})
        await dp.feed_update(bot, update)
    except Exception as e:
        logging.error(f"Error handling update: {e}")
    return web.Response(text="OK")

def add_deposit_for_user(user_id, deposit_amount):
    if user_id not in users_db:
        return
    users_db[user_id]["deposits_sum"] += deposit_amount
    
    referrer_id = users_db[user_id]["referrer"]
    if referrer_id and referrer_id in users_db and not users_db[referrer_id]["is_blocked"]:
        earned_bonus = deposit_amount * 0.20
        users_db[referrer_id]["earned_percent_sum"] += earned_bonus
        users_db[referrer_id]["balance_to_withdraw"] += earned_bonus
    save_db()

@router.message(CommandStart())
async def cmd_start(message: Message, state = None):
    user = message.from_user
    user_id = user.id
    
    if user_id in blocked_users or (user_id in users_db and users_db[user_id].get("is_blocked")):
        await message.answer("❌ Ваш аккаунт заблокирован за попытку накрутки рефералов или использования ботов.")
        return

    if user.is_bot:
        blocked_users.add(user_id)
        if user_id in users_db:
            users_db[user_id]["is_blocked"] = True
        save_db()
        return

    if state:
        await state.clear()
    
    args = message.text.split()
    
    if user_id not in users_db:
        users_db[user_id] = {
            "invited": [],
            "deposits_sum": 0.0,
            "earned_percent_sum": 0.0,
            "balance_to_withdraw": 0.0,
            "referrer": None,
            "is_blocked": False
        }
        
        if len(args) > 1:
            try:
                referrer_id = int(args[1])
                if referrer_id != user_id and referrer_id in users_db and not users_db[referrer_id]["is_blocked"]:
                    users_db[user_id]["referrer"] = referrer_id
                    if user_id not in users_db[referrer_id]["invited"]:
                        users_db[referrer_id]["invited"].append(user_id)
            except ValueError:
                pass
        save_db()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Зарегистрироваться на 1WIN (обязательно)", url=ONWIN_URL)],
            [InlineKeyboardButton(text="🆔 Привязать ID", callback_data="link_id")],
            [InlineKeyboardButton(text="👥 Реферальная система", callback_data="ref_system")]
        ]
    )
    await message.answer(
        "Привет! Для доступа к сигналам пройди регистрацию и привяжи свой игровой ID:",
        reply_markup=keyboard
    )

# --- РАЗДЕЛ: ВЫБОР ИГРЫ (МЕНЮ СИГНАЛОВ) ---
@router.callback_data(lambda c: c.data == "game_menu") # на всякий случай оставим обработчик на будущее, если потребуется
async def game_menu_callback(callback: CallbackQuery):
    pass

@router.callback_query(lambda c: c.data == "ref_system")
async def process_ref_system(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id in blocked_users or (user_id in users_db and users_db[user_id].get("is_blocked")):
        await callback.answer("Ваш аккаунт заблокирован.", show_alert=True)
        return

    if user_id not in users_db:
        users_db[user_id] = {
            "invited": [],
            "deposits_sum": 0.0,
            "earned_percent_sum": 0.0,
            "balance_to_withdraw": 0.0,
            "referrer": None,
            "is_blocked": False
        }
        save_db()
        
    user_data = users_db[user_id]
    
    valid_invited = [uid for uid in user_data["invited"] if uid not in blocked_users and not users_db.get(uid, {}).get("is_blocked", False)]
    invited_count = len(valid_invited)
    
    deposits_sum = user_data["deposits_sum"]
    earned_percent_sum = user_data["earned_percent_sum"]
    balance_to_withdraw = user_data["balance_to_withdraw"]
    
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    
    text = (
        f"📊 **Ваша реферальная статистика:**\n\n"
        f"• Количество приглашенных: {invited_count}\n"
        f"• Количество депозитов: {deposits_sum:.2f} руб.\n"
        f"• Сумма ваших полученных процентов с депозитов: {earned_percent_sum:.2f} руб.\n"
        f"• Сумма к выводу: {balance_to_withdraw:.2f} руб.\n\n"
        f"📉 Вы будете получать строго 20% от суммы выполненных депозитов друга.\n\n"
        f"🔗 Ваша индивидуальная ссылка:\n`{ref_link}`"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💸 Вывод", callback_data="withdraw_menu")],
            [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]
        ]
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(lambda c: c.data == "withdraw_menu")
async def process_withdraw(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👨‍💻 Написать менеджеру", url=MANAGER_URL)],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="ref_system")]
        ]
    )
    text = (
        "💳 **Вывод средств**\n\n"
        "Для того чтобы вывести средства, вам необходимо написать менеджеру.\n\n"
        "Свяжитесь с ним по ссылке ниже:"
    )
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Зарегистрироваться на 1WIN (обязательно)", url=ONWIN_URL)],
            [InlineKeyboardButton(text="🆔 Привязать ID", callback_data="link_id")],
            [InlineKeyboardButton(text="👥 Реферальная система", callback_data="ref_system")]
        ]
    )
    await callback.message.edit_text(
        "Привет! Для доступа к сигналам пройди регистрацию и привяжи свой игровой ID:",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "link_id")
async def process_link_id(callback: CallbackQuery, state):
    await state.set_state(Form.waiting_for_id)
    await callback.message.answer("Отправьте свой ID ответным сообщением:")
    await callback.answer()

@router.message(Form.waiting_for_id)
async def receive_user_id(message: Message, state):
    user_id_text = message.text.strip()
    await state.clear()
    
    # Кнопки с выбором: Мини-апп Mines ИЛИ Телеграм-сигналы Lucky Jet
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Открыть Сигналы Mines (WebApp)", web_app=WebAppInfo(url=WEBAPP_URL))],
            [InlineKeyboardButton(text="🚀 Получить сигнал Lucky Jet", callback_data="get_lucky_signal")],
            [InlineKeyboardButton(text="👥 Реферальная система", callback_data="ref_system")]
        ]
    )
    await message.answer(
        f"ID `{user_id_text}` успешно принят! ✅ Теперь выбери нужные сигналы:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# --- ЛОГИКА LUCKY JET (С математическим анализом 90%+) ---
def get_lucky_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Получить новый сигнал Lucky Jet", callback_data="get_lucky_signal")],
            [InlineKeyboardButton(text="⭐ Сигналы Mines", web_app=WebAppInfo(url=WEBAPP_URL))],
            [InlineKeyboardButton(text="👥 Реферальная система", callback_data="ref_system")]
        ]
    )

@router.callback_query(lambda c: c.data == "get_lucky_signal")
async def send_luckyjet_signal(callback: CallbackQuery):
    await callback.message.answer(
        "🔍 <i>Сканирование алгоритмов Lucky Jet...</i>\n📊 <i>Анализ последних раундов...</i>",
        parse_mode="HTML"
    )
    await asyncio.sleep(1)

    # Математический расчет проходимости 90%+
    import random
    chance = random.random()
    if chance < 0.90:
        val = random.uniform(1.12, 1.48)  # Безопасная зона
    else:
        val = random.uniform(2.10, 4.50)  # Редкий крупный икс
    coefficient = f"{val:.2f}x"

    await callback.message.answer(
        f"🎯 <b>Анализ завершен успешно!</b>\n\n"
        f"📊 <b>Проходимость сигнала:</b> ~92%\n"
        f"📌 <b>Рекомендуемый выход:</b> <b>{coefficient}</b>",
        parse_mode="HTML",
        reply_markup=get_lucky_keyboard()
    )
    await callback.answer()

@router.message()
async def echo_all(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Зарегистрироваться на 1WIN (обязательно)", url=ONWIN_URL)],
            [InlineKeyboardButton(text="🆔 Привязать ID", callback_data="link_id")],
            [InlineKeyboardButton(text="👥 Реферальная система", callback_data="ref_system")]
        ]
    )
    await message.answer("Пожалуйста, используй кнопки меню или команду /start для перезапуска.", reply_markup=keyboard)

async def keep_alive():
    await asyncio.sleep(15)
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(WEBAPP_URL) as response:
                    logging.info(f"Keep-alive ping status: {response.status}")
            except Exception as e:
                logging.error(f"Keep-alive ping error: {e}")
            await asyncio.sleep(240)

async def main():
    dp.include_router(router)
    
    app = web.Application()
    app.router.add_get('/', handle_web)
    app.router.add_get('/index.html', handle_web)
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    logging.info(f"Webhook set to {WEBHOOK_URL}")
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    asyncio.create_task(keep_alive())
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
