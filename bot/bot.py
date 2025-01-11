import os
import sys
import logging
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties

from bot.config import BOT_TOKEN, setup_logger
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

async def main() -> None:
    global bot
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    bot_logger.info('Bot is starting...')
    asyncio.run(main())
