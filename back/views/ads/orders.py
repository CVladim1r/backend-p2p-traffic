from pydantic import BaseModel, UUID4, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from back.models.enums import Categories, AdStatus, DealStatus, TransactionCurrencyType


class AdCreate(BaseModel):
    category: Categories
    title: str
    description: str
    
    currency_type: TransactionCurrencyType
    link_to_channel: str
    maximum_traffic: int

    price: float # ] = Field(gt=0, description="Price must be greater than 0")
    guaranteed_traffic: bool
    minimum_traffic: int
    conditions: str
    is_paid_promotion: bool

class AdCreateOut(BaseModel):
    uuid: UUID4
    created_at: datetime

    class Config:
        orm_mode = True


class AdOut(BaseModel):
    uuid: UUID4
    category: Categories
    title: str
    description: str
    price: Optional[float]
    guaranteed_traffic: bool
    minimum_traffic: int | None
    maximum_traffic: int | None
    currency_type: Optional[TransactionCurrencyType]
    link_to_channel: Optional[str]
    conditions: str
    is_paid_promotion: bool
    status: AdStatus

    user: UUID4
    user_name: str
    user_photo_url: str
    user_deals: int
    user_rating: float
    user_vip: bool

    # created_at: datetime
    # updated_at: datetime

    class Config:
        orm_mode = True


class DealCreate(BaseModel):
    ad_uuid: UUID4


class DealOut(BaseModel):
    uuid: UUID4
    ad_uuid: UUID4
    buyer_id: int
    seller_id: int
    status: DealStatus
    is_frozen: bool
    support_request: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
