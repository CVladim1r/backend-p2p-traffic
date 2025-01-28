from pydantic import BaseModel, UUID4
from typing import Optional
from decimal import Decimal
from datetime import datetime
from back.models.enums import Categories, AdStatus, DealStatus


class AdCreate(BaseModel):
    category: Categories
    title: str
    description: str
    price: Decimal
    guaranteed_traffic: bool
    minimum_traffic: Optional[int]
    conditions: str
    execution_time: str
    is_paid_promotion: bool


class AdOut(BaseModel):
    uuid: UUID4
    category: Categories
    title: str
    description: str
    price: Decimal
    guaranteed_traffic: bool
    minimum_traffic: Optional[int]
    conditions: str
    execution_time: str
    is_paid_promotion: bool
    status: AdStatus
    created_at: datetime
    updated_at: datetime

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
