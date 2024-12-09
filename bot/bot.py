from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiohttp import ClientSession

BOT_TOKEN = "your-telegram-bot-token"
MINIAPP_URL = "https://example.com/miniapp"
METRICS_API = "http://localhost:8000/metrics"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: Message):
    async with ClientSession() as session:
        await session.post(METRICS_API, json={"event_type": "start", "user_id": str(message.from_user.id)})
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть MiniApp", url=MINIAPP_URL)]
        ]
    )
    await message.answer("Добро пожаловать! Нажмите кнопку ниже, чтобы открыть MiniApp.", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)
