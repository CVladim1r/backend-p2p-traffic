from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserMainPageIn(BaseModel):
    tg_id: int

class UserMainPageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    tg_id: int
    username: str | None

    rating: float
    balance: float
    total_sales: float
    referral_id: UUID | None
    is_vip: bool
    created_at: str
    updated_at: str


class CreateUserRequest(BaseModel):
    tg_id: int
    username: str | None = None
    profile_photo: str | None = None

class UserMainData(BaseModel):
    uuid: UUID
    tg_id: int
    username: str | None

    rating: float
    balance: float
    total_sales: float
    referral_id: UUID | None
    is_vip: bool
    created_at: str
    updated_at: str

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

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    tg_id: int
    username: Optional[str] = None
    is_premium: Optional[bool] = None
    created_at: datetime

class UserOut(BaseModel):
    uuid: UUID
    tg_id: int
    username: str
    profile_photo: str
