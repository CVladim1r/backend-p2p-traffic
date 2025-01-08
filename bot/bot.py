import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from aiohttp import ClientSession
from dotenv import load_dotenv
import logging

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MINIAPP_URL = os.getenv("MINIAPP_URL")
METRICS_API = os.getenv("BACK_METRICS_API", "http://localhost:8000/metrics")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: Message):
    async with ClientSession() as session:
        try:
            await session.post(METRICS_API, json={"event_type": "start", "user_id": str(message.from_user.id)})
        except Exception as e:
            logging.error(f"Error posting metrics: {e}")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть MiniApp", web_app=WebAppInfo(url=MINIAPP_URL))]
        ]
    )

    await message.answer(
        "🎉 Горячо приветствуем тебя, дружище!👋\n\n"
        "P2P JUST-AD- это 🚀 уникальная маркетинговая экосистема по купле-продаже рекламы, "
        "которая охватывает весь рынок Telegram 📱. Ты прямо сейчас находишься в самом центре этого процесса!\n\n"
        "Почему тебе будет выгоднее работать именно с нами, а не с каким-то Васей из крипто-коммьюнити?\n\n"
        "✨ 1. Полная защищенная анонимность. Даже Пентагон не сможет пробить твой профиль.\n"
        "💸 2. Комиссия-лилипут. Настолько маленькая, что шутить об этом будет слишком низко.\n"
        "🛡️ 3. Безопасность превыше всего - слово SCAM для нас не существует.\n"
        "💰 4. Мега-удобная оплата: примем любую твою криптовалюту.\n"
        "📈 5. Большущая клиентская база, которая с каждым днем становится все упитаннее, увеличивая колоссальный спрос на рекламу 📊.\n"
        "Если ты ставишь в приоритет быстроту, комфорт и надежный результат, то наш маркетплейс закроет все эти потребности на 5+.\n\n"
        "Давай начнем твое путешествие прямо сейчас! 🚀\n", reply_markup=keyboard
    )


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
