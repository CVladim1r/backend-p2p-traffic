from datetime import timezone, datetime
from typing import Any, Dict, List

from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from back.controllers.base import BaseUserController, T
from back.errors import APIExceptionModel, APIException
from back.models import Users

import logging


class UserController(BaseUserController):
    model = Users

    @classmethod
    async def get_by_tg_id(cls, tg_id: int) -> T | None:
        return await cls.model.get_or_none(tg_id=tg_id)

    @classmethod
    async def get_user_with_prizes(cls, tg_id: int) -> Users:
        return await cls.model.get_or_none(tg_id=tg_id).prefetch_related('prizes')

    @classmethod
    async def list(cls, page: int = 0, limit: int = 100) -> List[T]:
        models = await cls.model.all().limit(limit).offset(page * limit)
        return models

    @classmethod
    async def get_main_page_user_data(cls, tg_id: int) -> Users | APIExceptionModel:
        return await cls.model.get(tg_id=tg_id)

    @classmethod
    async def update_user_data(cls, tg_id: int, update_data: Dict[str, Any]) -> Users:
        return await cls.update_user_by_tg_id(tg_id, update_data)

    @classmethod
    async def add_user_if_not_exists(cls, tg_id: int, username: str):
        try:
            user = await Users.get(tg_id=tg_id)
        except DoesNotExist:
            try:
                user = await Users.create(
                    tg_id=tg_id,
                    username=username,
                    rating=5.00,
                    total_sales=0.0,
                    is_vip=False,
                    last_login=datetime.now(timezone.utc),
                    created_at=datetime.now(timezone.utc),
                )
                logging.info(f"User created successfully: {tg_id}, {username}")
            except Exception as error:
                logging.error(f"Error creating user {tg_id}, {username}: {error}")
                raise APIException(f"Create user failed: {error}", 400)
        return user