from typing import Any, Dict, List

from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from back.controllers.base import BaseUserController, T
from back.errors import APIExceptionModel
from back.models import User


class UserController(BaseUserController):
    model = User

    @classmethod
    async def get_by_tg_id(cls, tg_id: int) -> T | None:
        return await cls.model.get_or_none(tg_id=tg_id)

    @classmethod
    async def list(cls, page: int = 0, limit: int = 100) -> List[T]:
        models = await cls.model.all().limit(limit).offset(page * limit)
        return models

    @classmethod
    async def get_main_page_user_data(cls, tg_id: int) -> User | APIExceptionModel:
        return await cls.model.get(tg_id=tg_id)

    @classmethod
    async def update_user_data(cls, tg_id: int, update_data: Dict[str, Any]) -> User:
        return await cls.update_user_by_tg_id(tg_id, update_data)
