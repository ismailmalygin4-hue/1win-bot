import os
import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Твой актуальный токен
TOKEN = "8818268231:AAEi1MEo0v_En13hmHcDApF-9unmT1S3jJ8"
PORT = int(os.getenv("PORT", 10000))

# Ссылка на веб-приложение на Render
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://1win-bot-1.onrender.com")

# Ссылка на 1WIN
ONWIN_URL = "https://one-vv8000.com/?open=register&p=i390"

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

# HTML-страница игры Mines для Mini App
HTML_CONTENT = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mines Signals</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {{
            background-color: #0f1923;
            color: #ffffff;
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 20px;
        }}
        h2 {{ color: #00ffcc; margin-bottom: 10px; }}
        .settings {{
            margin: 15px 0;
            font-size: 16px;
        }}
        select {{
            background: #1b2838;
            color: #fff;
            border: 1px solid #00ffcc;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 16px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 8px;
            max-width: 320px;
            margin: 20px auto;
        }}
        .cell {{
            aspect-ratio: 1;
            background: #1b2838;
            border: 2px solid #2a475e;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            transition: 0.3s;
        }}
        .cell.active {{
            background: #00ffcc;
            border-color: #fff;
            box-shadow: 0 0 10px #00ffcc;
        }}
        button.btn {{
            background: linear-gradient(135deg, #00ffcc, #00b386);
            color: #0f1923;
            border: none;
            padding: 12px 25px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 15px;
            width: 100%;
            max-width: 320px;
        }}
        button.btn-win {{
            background: linear-gradient(135deg, #ff9900, #ff5500);
            color: #ffffff;
            margin-top: 10px;
            text-decoration: none;
        }}
        button.btn:active {{ transform: scale(0.98); }}
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

    <button class="btn" onclick="getSignal()">ВЫДАТЬ СИГНАЛ</button>
    
    <a href="{ONWIN_URL}" target="_blank" style="text-decoration: none;">
        <button class="btn btn-win">ПЕРЕЙТИ НА 1WIN</button>
    </a>

    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();

        const gridElement = document.getElementById('grid');
        const totalCells = 25;

        for (let i = 0; i < totalCells; i++) {{
            const cell = document.createElement('div');
            cell.classList.add('cell');
            gridElement.appendChild(cell);
        }}

        function getSignal() {{
            const mines = parseInt(document.getElementById('minesCount').value);
            const cells = document.querySelectorAll('.cell');
            
            cells.forEach(c => c.classList.remove('active'));
            cells.forEach(c => c.innerHTML = '');

            let safeCount = totalCells - mines;
            let targetCount = Math.min(safeCount, 5); 
            
            let opened = [];
            while(opened.length < targetCount) {{
                let randomIndex = Math.floor(Math.random() * totalCells);
                if(!opened.includes(randomIndex)) {{
                    opened.push(randomIndex);
                }}
            }}

            opened.forEach(index => {{
                cells[index].classList.add('active');
                cells[index].innerHTML = '⭐';
            }});

            if (tg.HapticFeedback) {{
                tg.HapticFeedback.impactOccurred('medium');
            }}
        }}
    </script>
</body>
</html>
"""

async def handle_web(request):
    return web.Response(text=HTML_CONTENT, content_type='text/html')

@router.message(CommandStart())
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💣 Открыть игру Mines", web_app=WebAppInfo(url=WEBAPP_URL))],
            [InlineKeyboardButton(text="🎯 Зарегистрироваться на 1WIN", url=ONWIN_URL)]
        ]
    )
    await message.answer(
        "Привет! Нажми кнопку ниже, чтобы запустить мини-апп с сигналами или перейти на 1WIN:",
        reply_markup=keyboard
    )

async def main():
    dp.include_router(router)
    
    app = web.Application()
    app.router.add_get('/', handle_web)
    app.router.add_get('/index.html', handle_web)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logging.info(f"Web server started on port {PORT}")

    # Сбрасываем вебхуки и зависшие сессии
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Небольшая пауза для полного завершения старых подключений
    await asyncio.sleep(3)
    
    await dp.start_polling(bot, close_bot_session=True)

if __name__ == "__main__":
    asyncio.run(main())
