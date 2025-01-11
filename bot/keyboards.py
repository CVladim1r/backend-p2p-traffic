from aiogram.types import InlineKeyboardButton, WebAppInfo, InlineKeyboardMarkup

from config import MINIAPP_URL

web_app_info = WebAppInfo(url=MINIAPP_URL)
buttons = [
    [
        InlineKeyboardButton(text='Telegram Channel', url='https://t.me/'),
        InlineKeyboardButton(text='Join X', url='https://x.com/'),
    ],
    [InlineKeyboardButton(text='Play', web_app=web_app_info)],
]
start_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
