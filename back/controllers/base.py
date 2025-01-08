from typing import Any, Dict, List, Type, TypeVar
from uuid import UUID

from tortoise.exceptions import DoesNotExist

from satoshi.errors import APIException

T = TypeVar("T")


class BaseUserController:
    model: Type[T]

    @classmethod
    async def list(cls, page: int = 0, limit: int = 100) -> List[T]:
        models = await cls.model.all().limit(limit).offset(page * limit)
        return models

    @classmethod
    async def get_user_by_tg_id(cls, tg_id: int, *fields: str) -> T | None:
        try:
            if len(fields) > 0:
                return await cls.model.get(tg_id=tg_id).only(*fields)
            else:
                return await cls.model.get(tg_id=tg_id)
        except DoesNotExist:
            raise APIException("Not found", 404)

    @classmethod
    async def get_user_by_uuid(cls, user_uuid: UUID, *fields: str) -> T | None:
        try:
            return await cls.model.get(uuid=user_uuid).only(*fields)
        except DoesNotExist:
            raise APIException("Not found", 404)

    @classmethod
    async def update_user_by_tg_id(cls, tg_id: int, update_data: Dict[str, Any]) -> T:
        try:
            user = await cls.model.get(tg_id=tg_id)
            for field, value in update_data.items():
                setattr(user, field, value)
            await user.save()
            return user
        except DoesNotExist:
            raise APIException("User not found", 404)

    # @classmethod
    # async def get(cls, object_id: UUID, user: User):
    #     raise APIException("Not found", 404)
    #
    # @classmethod
    # async def create(cls, object_create_in: BaseModel, user: User):
    #     raise APIException("Not found", 404)
    #
    # @classmethod
    # async def update(cls, object_id: UUID, object_update_in: BaseModel, user: User):
    #     raise APIException("Not found", 404)
    #
    # @classmethod
    # async def delete(cls, object_id: UUID, user: User):
    #     raise APIException("Not found", 404)
