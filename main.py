import os
import logging
import asyncio
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, Update
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

TOKEN = "8818268231:AAHMhMwPrBDP2JGTsajUrHqXBgXPR0e4HhU"
PORT = int(os.getenv("PORT", 10000))
WEBAPP_URL = "https://onewin-bot-1.onrender.com"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBAPP_URL}{WEBHOOK_PATH}"
ONWIN_URL = "https://one-vv8631.com/?open=register&p=i390"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

class Form(StatesGroup):
    waiting_for_id = State()

HTML_CONTENT = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mines Signals</title>
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

@router.message(CommandStart())
async def cmd_start(message: Message, state = None):
    if state:
        await state.clear()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Зарегистрироваться на 1WIN (обязательно)", url=ONWIN_URL)],
            [InlineKeyboardButton(text="🆔 Привязать ID", callback_data="link_id")]
        ]
    )
    await message.answer(
        "Привет! Для доступа к сигналам пройди регистрацию и привяжи свой игровой ID:",
        reply_markup=keyboard
    )

@router.callback_query(lambda c: c.data == "link_id")
async def process_link_id(callback: CallbackQuery, state):
    await state.set_state(Form.waiting_for_id)
    await callback.message.answer("Отправьте свой ID ответным сообщением:")
    await callback.answer()

@router.message(Form.waiting_for_id)
async def receive_user_id(message: Message, state):
    user_id_text = message.text.strip()
    await state.clear()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Открыть Сигналы 1win", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
    )
    await message.answer(
        f"ID `{user_id_text}` успешно принят! ✅ Теперь ты можешь запустить мини-апп с сигналами:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.message()
async def echo_all(message: Message):
    await message.answer("Пожалуйста, используй команду /start для перезапуска меню.")

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
