from uuid import UUID
from typing import Optional, Annotated
from decimal import Decimal
from datetime import datetime
from pydantic.types import List
from pydantic import BaseModel, UUID4, Field

from back.models.enums import (
    CategoriesAds, 
    AdStatus, 
    DealStatus, 
    TypeUserAcquisition,
    TransactionCurrencyType,
    PrizeType
)


class AdCreate(BaseModel):
    category: CategoriesAds
    ad_type: TypeUserAcquisition
    title: str
    description: str
    currency_type: TransactionCurrencyType
    user_currency_for_payment: TransactionCurrencyType
    link_to_channel: str
    maximum_traffic: int
    price: float
    guaranteed_traffic: int
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
    category: CategoriesAds
    ad_type: TypeUserAcquisition
    title: str
    description: str
    price: Optional[float]
    guaranteed_traffic: int
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

    class Config:
        orm_mode = True


class AdOut(BaseModel):
    uuid: UUID4
    category: CategoriesAds
    title: str
    description: str
    price: Optional[float]
    guaranteed_traffic: int
    minimum_traffic: int | None
    maximum_traffic: int | None
    currency_type: Optional[TransactionCurrencyType]
    link_to_channel: Optional[str]
    conditions: str
    is_paid_promotion: bool
    status: AdStatus
    ad_type: TypeUserAcquisition
    
    user: UUID4
    user_name: str
    user_photo_url: str
    user_deals: int
    user_rating: float
    user_vip: bool

    class Config:
        orm_mode = True

class DealCreate(BaseModel):
    ad_uuid: UUID4

class PinChatRequest(BaseModel):
    is_pinned: bool

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

class ChatOut(BaseModel):
    uuid: UUID4
    is_pinned: bool
    messages: List[ChatMessage]
    buyer_name: str
    seller_name: str
    seller_photo_url: str
    buyer_photo_url: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ChatPinOut(BaseModel):
    uuid: UUID4
    is_pinned: bool

    class Config:
        orm_mode = True


class ChatAllOut(BaseModel):
    uuid: UUID4
    deal_uuid: UUID4
    is_pinned: bool
    counterpart_id: UUID4
    counterpart_isvip: bool
    counterpart_photo: str
    counterpart_username: str
    user_role: str
    last_message_text: Optional[str] = None
    last_message_sender_id: Optional[UUID4] = None
    last_message_timestamp: Optional[datetime] = None

    class Config:
        orm_mode = True

class DealsOut(BaseModel):
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

    class Config:
        orm_mode = True
        from_attributes=True

class DealOutCOMPLETE(BaseModel):
    uuid: UUID4
    status: DealStatus
    price: Decimal 
    currency: TransactionCurrencyType
    is_frozen: bool
    support_request: bool


    class Config:
        orm_mode = True
        from_attributes=True

class DealOut(BaseModel):
    uuid: UUID4
    buyer_id: UUID4
    seller_id: UUID4
    status: DealStatus
    price: Decimal 
    currency: TransactionCurrencyType
    is_frozen: bool
    buyer_confirms: bool
    seller_confirms: bool

    buyer_review: bool
    seller_review: bool

    support_request: bool

    # created_at: datetime
    # updated_at: datetime

    class Config:
        orm_mode = True

class ReviewCreate(BaseModel):
    rating: Annotated[int, Field(ge=1, le=5)]
    comment: str | None = Field(None, max_length=500)

class ReviewOut(BaseModel):
    uuid: UUID4
    deal_uuid: UUID4
    reviewer_id: UUID4
    reviewed_user_id: UUID4
    rating: int
    comment: str | None
    created_at: str

    seller_review: bool
    buyer_review: bool