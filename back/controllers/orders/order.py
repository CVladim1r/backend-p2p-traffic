import logging

from uuid import UUID
from typing import List
from decimal import Decimal
from datetime import datetime

from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from back.controllers.base import BaseUserController
from back.controllers.user import UserController
from back.errors import APIException
from back.models import Ads, Deals, Chats, Users
from back.models.enums import AdStatus, DealStatus
from back.utils.cryptobot import crypto_service
from back.views.ads import (
    AdOut, 
    AdCreate, 
    DealOut,
    DealCreate,
    ChatMessage,
    ChatMessageCreate,
    ChatOut,
)

class OrderController(BaseUserController):
    @staticmethod
    async def calculate_commission(price: Decimal) -> Decimal:
        rates = await crypto_service.get_exchange_rates()
        ton_rate = next(r for r in rates if r.source == "TON" and r.target == "USD")
        return (price * Decimal('0.10')) / Decimal(ton_rate.rate)
    
    @staticmethod
    async def create_ad(ad_data: AdCreate, user_in):
        user = await Users.get(tg_id=user_in.tg_id)
        if not user:
            raise APIException(detail="User not found", status_code=404)

        def_status = AdStatus.ACTIVE
        
        ad = await Ads.create(
            user_id=user,
            category=ad_data.category,
            title=ad_data.title,
            description=ad_data.description,
            price=ad_data.price,
            guaranteed_traffic=ad_data.guaranteed_traffic,
            minimum_traffic=ad_data.minimum_traffic,
            maximum_traffic=ad_data.maximum_traffic,
            link_to_channel=ad_data.link_to_channel,
            currency_type=ad_data.currency_type,
            conditions=ad_data.conditions,
            is_paid_promotion=ad_data.is_paid_promotion,
            status=def_status,
        )
        return ad
    
    @staticmethod
    async def get_ads(category: str = None) -> List[AdOut]:
        query = Ads.all().prefetch_related("user_id")
        
        if category:
            query = query.filter(category=category)

        ads = await query
        result = []
        for ad in ads:
            user = ad.user_id

            ad_out = AdOut(
                uuid=ad.uuid,
                category=ad.category,
                title=ad.title,
                description=ad.description,
                price=ad.price,
                guaranteed_traffic=ad.guaranteed_traffic,
                minimum_traffic=ad.minimum_traffic,
                maximum_traffic=ad.maximum_traffic,
                currency_type=ad.currency_type,
                link_to_channel=ad.link_to_channel,
                conditions=ad.conditions,
                is_paid_promotion=ad.is_paid_promotion,
                status=ad.status,
                user=user.uuid,
                user_name=user.username,
                user_photo_url=user.profile_photo,
                user_deals=int(user.total_sales),
                user_rating=float(user.rating) if user.rating else 0.0,
                user_vip=user.is_vip,
            )

            result.append(ad_out)
        return result

    @staticmethod
    async def get_ad(ad_uuid: str) -> Ads:
        try:
            ad = await Ads.get(uuid=ad_uuid)
        except DoesNotExist:
            raise APIException(detail="Ad not found", status_code=404)
        return ad

    @staticmethod
    async def create_deal(deal_data: DealCreate, user_id: int) -> Deals: 
        user = await UserController.get_by_tg_id(user_id)
        # logging.info(f"user_id: {user_id}, user: {user}")

        try:
            ad = await Ads.get(uuid=deal_data.ad_uuid).prefetch_related("user_id")
        except DoesNotExist:
            raise APIException(detail="Ad not found", status_code=404)
        
        # logging.info(ad.user_id)

        logging.info(f"byer={user.uuid}, seller_id={ad.user_id.uuid}, ad_uuid={ad.uuid}")

        if ad.user_id == user.tg_id:
            raise APIException(detail="You cannot buy your own ad", status_code=400)    

        async with in_transaction():
            deal = await Deals.create(
                ad_uuid=ad.uuid,
                buyer_id=user.uuid,
                seller_id=ad.user_id.uuid,
                price=ad.price,
                status=DealStatus.PENDING,
                currency=ad.currency_type
            )

            await Chats.create(deal=deal)
        return deal
    
    @staticmethod
    async def send_chat_message(deal_uuid: UUID, message_data: ChatMessageCreate, sender_id: UUID) -> ChatMessage:
        deal = await Deals.get(uuid=deal_uuid).prefetch_related("buyer_id", "seller_id")
        sender = await UserController.get_by_uuid(sender_id)
        
        if sender.uuid not in [deal.buyer_id.uuid, deal.seller_id.uuid]:
            raise APIException(detail="Access denied", status_code=403)
        
        chat = await Chats.get(deal=deal)
        new_message = {
            "sender_id": str(sender.uuid),
            "text": message_data.text,
            "timestamp": datetime.utcnow().isoformat()
        }
        chat.messages.append(new_message)
        await chat.save()
        
        return ChatMessage(**new_message)

    @staticmethod
    async def get_deal_chat(deal_uuid: UUID, user_id: UUID) -> ChatOut:
        deal = await Deals.get(uuid=deal_uuid).prefetch_related("buyer_id", "seller_id")
        user = await UserController.get_by_uuid(user_id)
        
        if user.uuid not in [deal.buyer_id.uuid, deal.seller_id.uuid]:
            raise APIException(detail="Access denied", status_code=403)
        
        chat = await Chats.get(deal=deal)
        return await ChatOut.from_tortoise_orm(chat)