import datetime
from typing import Tuple, Optional

import aiohttp
from aiogram.types import InlineKeyboardMarkup

from config import setup_logger
from constants import BACKEND_URLS, MESSAGES
from keyboards import start_keyboard

bot_logger = setup_logger('Telegram Bot')
keyboard = start_keyboard


async def success_start_msg(username: str) -> str:
    msg = (
        f"🎉 Горячо приветствуем тебя, дружище {username}!👋\n\n"
        "P2P JUST-AD — это 🚀 уникальная маркетинговая экосистема по купле-продаже рекламы, "
        "которая охватывает весь рынок Telegram 📱. Ты прямо сейчас находишься в самом центре этого процесса!\n\n"
        "Почему тебе будет выгоднее работать именно с нами, а не с каким-то Васей из крипто-коммьюнити?\n\n"
        "✨ 1. Полная защищенная анонимность. Даже Пентагон не сможет пробить твой профиль.\n"
        "💸 2. Комиссия-лилипут. Настолько маленькая, что шутить об этом будет слишком низко.\n"
        "🛡️ 3. Безопасность превыше всего — слово SCAM для нас не существует.\n"
        "💰 4. Мега-удобная оплата: примем любую твою криптовалюту.\n"
        "📈 5. Большущая клиентская база, которая с каждым днем становится все упитаннее, увеличивая колоссальный спрос на рекламу 📊.\n\n"
        "Если ты ставишь в приоритет быстроту, комфорт и надежный результат, то наш маркетплейс закроет все эти потребности на 5+.\n\n"
        "Давай начнем твое путешествие прямо сейчас! 🚀"
    )
    return msg


# async def log_new_user(username, ref_check):
#     bot_logger.info(f'New user {username=} joined.')


async def get_jwt_token(username: str, is_premium: bool, tg_id: int) -> str:
    connector = aiohttp.TCPConnector(limit_per_host=5)
    async with aiohttp.ClientSession(trust_env=True, connector=connector) as session:
        auth_url = BACKEND_URLS.get('auth')
        today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        payload = {
            "init_data_raw": {
                "auth_date": today,
                "hash": "mock_hash",
                "query_id": "mock_id",
                "user": {
                    "allows_write_to_pm": "true",
                    "first_name": "mock_first_name",
                    "id": tg_id,
                    "is_premium": is_premium,
                    "language_code": "en",
                    "last_name": "mock_last_name",
                    "username": username,
                },
            },
            "init_ton": {"address": "string", "signature": "full"},
            "auth_type": "telegram",
        }

        bot_logger.info(f'payload: {payload}')


        # async with session.post(auth_url, json=payload, ssl=False) as response:
        #     response_data = await response.json()
        #     if response.status != 200:
        #         bot_logger.error(f"Failed to obtain JWT token: {await response.text()}")
        #         raise Exception("Failed to obtain JWT token")
        #     return response_data.get('access_token')

        async with session.post(auth_url, json=payload, ssl=False) as response:
            if response.status != 200:
                response_text = await response.text()
                bot_logger.error(f"Failed to obtain JWT token: {response.status}, {response_text}")
                raise Exception(f"Failed to obtain JWT token: {response_text}")
            response_data = await response.json()
            return response_data.get('access_token')





async def create_user_request(
    session: aiohttp.ClientSession, payload: dict, headers: dict
) -> Optional[dict]:
    create_user_link = BACKEND_URLS.get('create_user')
    bot_logger.info(f"Create user URL: {create_user_link}")
    async with session.post(create_user_link, json=payload, headers=headers, ssl=False) as response:
        if response.status == 401:
            return None
        return await response.json()


async def start_user_get_or_create(
    tg_id: int, username: str, is_premium: bool | None
) -> Tuple[str, InlineKeyboardMarkup | None]:
    token = await get_jwt_token(username=username, is_premium=is_premium, tg_id=tg_id, )
    headers = {'Authorization': f'Bearer {token}'}

    connector = aiohttp.TCPConnector(limit_per_host=5)
    async with aiohttp.ClientSession(trust_env=True, connector=connector) as session:
        payload = {"tg_id": tg_id, "username": username, "is_premium": is_premium}
       

        response_data = await create_user_request(session, payload, headers)
        if response_data is None:
            bot_logger.error("Create user response_data is None, retrying request.")
            token = await get_jwt_token(username=username, is_premium=is_premium, tg_id=tg_id)
            headers = {'Authorization': f'Bearer {token}'}
            response_data = await create_user_request(session, payload, headers)

        if response_data is None or 'tg_id' not in response_data:
            reply_text = MESSAGES.get('error')

            bot_logger.info(f'response_data: {response_data}')


            bot_logger.error("Failed to create user after token refresh attempt.")
            return reply_text, None

        # await log_new_user(username=username)
        reply_text = await success_start_msg(username)
        return reply_text, keyboard
