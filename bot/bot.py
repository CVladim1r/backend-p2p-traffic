import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiohttp import ClientSession
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MINIAPP_URL = os.getenv("MINIAPP_URL", "https://miniapp")
METRICS_API = os.getenv("METRICS_API", "http://localhost:8000/metrics")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: Message):
    async with ClientSession() as session:
        try:
            await session.post(METRICS_API, json={"event_type": "start", "user_id": str(message.from_user.id)})
        except Exception as e:
            print(f"Error posting metrics: {e}")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть MiniApp", url=MINIAPP_URL)]
        ]
    )
    await message.answer("Добро пожаловать! Нажмите кнопку ниже, чтобы открыть MiniApp.", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
