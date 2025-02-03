from typing import Optional
from decimal import Decimal
from datetime import datetime
from pydantic.types import List
from pydantic import BaseModel, UUID4

from back.models.enums import (
    Categories, 
    AdStatus, 
    DealStatus, 
    TransactionCurrencyType
)


class AdCreate(BaseModel):
    category: Categories
    title: str
    description: str
    
    currency_type: TransactionCurrencyType
    link_to_channel: str
    maximum_traffic: int

    price: float
    guaranteed_traffic: bool
    minimum_traffic: int
    conditions: str
    is_paid_promotion: bool

class AdCreateOut(BaseModel):
    uuid: UUID4
    created_at: datetime

    class Config:
        orm_mode = True

class AdOutOne(BaseModel):
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

# class DealOut(BaseModel):
#     uuid: UUID4
#     ad_uuid: UUID4
#     buyer_id: int
#     seller_id: int
#     status: DealStatus
#     is_frozen: bool
#     support_request: bool
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         orm_mode = True

class ChatMessage(BaseModel):
    sender_tg_id: int
    sender_name: str
    sender_uuid: UUID4 
    text: str
    timestamp: datetime

class ChatMessageGet(BaseModel):
    sender_uuid: UUID4 
    text: str
    timestamp: datetime

class ChatMessageCreate(BaseModel):
    text: str
    sender_id: UUID4 

class ChatOut(BaseModel):
    uuid: UUID4
    # deal_uuid: UUID4
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class DealOut(BaseModel):
    uuid: UUID4
    ad_uuid: UUID4
    buyer_id: UUID4
    seller_id: UUID4
    status: DealStatus
    price: Decimal 
    currency: TransactionCurrencyType
    is_frozen: bool
    support_request: bool
    created_at: datetime
    updated_at: datetime
    # chat: Optional[ChatOut] = None  # Cвязь с чатом

    class Config:
        orm_mode = True