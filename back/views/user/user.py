from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserMainPageIn(BaseModel):
    tg_id: int

class StartUserIn(BaseModel):
    tg_id: int
    username: str
    is_premium: bool

class StartUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    tg_id: int
    username: str
    is_premium: Optional[bool] = None
    created_at: datetime

class RefUserIn(BaseModel):
    tg_id: int
    referrer_uuid: UUID
    is_premium: bool
