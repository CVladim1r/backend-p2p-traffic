import os
import sys
import logging
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiohttp import ClientSession

from bot.config import BOT_TOKEN, MINIAPP_URL, METRICS_API, setup_logger
from bot.utils import start_user_get_or_create

logging.basicConfig(level=logging.INFO)

bot_logger = setup_logger('Telegram Bot')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    tg_id = int(message.from_user.id)
    username = str(message.from_user.username)
    is_premium = message.from_user.is_premium or False
    referred_user_tg_id = (
        message.text.split(maxsplit=1)[1] if len(message.text.split(maxsplit=1)) > 1 else None
    )
    reply_text, keyboard = await start_user_get_or_create(
        tg_id=tg_id,
        username=username,
        is_premium=is_premium,
        referral_uuid=referred_user_tg_id,
    )
    await message.answer(text=reply_text, reply_markup=keyboard)



# @dp.message(Command("start"))
# async def start(message: Message):
#     async with ClientSession() as session:
#         try:
#             await session.post(METRICS_API, json={"event_type": "start", "user_id": str(message.from_user.id)})
#         except Exception as e:
#             logging.error(f"Error posting metrics: {e}")

#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(text="Открыть MiniApp", web_app=WebAppInfo(url=MINIAPP_URL))]
#         ]
#     )

#     await message.answer(
#         "🎉 Горячо приветствуем тебя, дружище!👋\n\n"
#         "P2P JUST-AD- это 🚀 уникальная маркетинговая экосистема по купле-продаже рекламы, "
#         "которая охватывает весь рынок Telegram 📱. Ты прямо сейчас находишься в самом центре этого процесса!\n\n"
#         "Почему тебе будет выгоднее работать именно с нами, а не с каким-то Васей из крипто-коммьюнити?\n\n"
#         "✨ 1. Полная защищенная анонимность. Даже Пентагон не сможет пробить твой профиль.\n"
#         "💸 2. Комиссия-лилипут. Настолько маленькая, что шутить об этом будет слишком низко.\n"
#         "🛡️ 3. Безопасность превыше всего - слово SCAM для нас не существует.\n"
#         "💰 4. Мега-удобная оплата: примем любую твою криптовалюту.\n"
#         "📈 5. Большущая клиентская база, которая с каждым днем становится все упитаннее, увеличивая колоссальный спрос на рекламу 📊.\n"
#         "Если ты ставишь в приоритет быстроту, комфорт и надежный результат, то наш маркетплейс закроет все эти потребности на 5+.\n\n"
#         "Давай начнем твое путешествие прямо сейчас! 🚀\n", reply_markup=keyboard
#     )


async def main() -> None:
    global bot
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    bot_logger.info('Bot is starting...')
    asyncio.run(main())
