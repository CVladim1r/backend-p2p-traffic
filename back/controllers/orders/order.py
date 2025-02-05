import logging

from uuid import UUID
from typing import List
from decimal import Decimal
from datetime import datetime, timezone

from tortoise.expressions import Q
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
    DealsOut,
    DealCreate,
    ChatMessage,
    ChatAllOut,
    ChatMessageCreate,
    ChatOut,
)

class OrderController(BaseUserController):
    @staticmethod
    async def calculate_commission(price: Decimal) -> Decimal:
        rates = await crypto_service.get_exchange_rates()
        ton_rate = next(r for r in rates if r.source == "TON" and r.target == "USD")
        return (price * Decimal('0.10')) / Decimal(ton_rate.rate)


    """
    ------------ ADS ------------
    """

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


    """
    ----------- DEALS -----------
    """

    @staticmethod
    async def create_deal(deal_data: DealCreate, user_id: int) -> Deals: 
        user = await UserController.get_by_tg_id(user_id)

        try:
            ad = await Ads.get(uuid=deal_data.ad_uuid).prefetch_related("user_id")
        except DoesNotExist:
            raise APIException(error="Ad not found", status_code=404)
        
        if ad.user_id == user.tg_id:
            raise APIException(error="You cannot buy your own ad", status_code=400)    

        async with in_transaction():
            deal = await Deals.create(
                ad_uuid=ad,
                buyer_id=user,
                seller_id=ad.user_id,
                price=ad.price,
                status=DealStatus.PENDING,
                currency=ad.currency_type
            )
            await Chats.create(deal=deal)
            chat = await Chats.get(deal=deal)
            new_message = {
                "sender_name": "admin",
                "sender_tg_id": "0",
                "sender_uuid": "3f048ec2-0e18-4d53-8556-21aed104fa2f",
                "text": "Вы успешно разместили ордер. Выполните условия и дождитесь подтверждения обеих сторон. В случае спорной ситуации открывайте спор. Мы поможем Вам разобраться в ситуации.",
                "timestamp": datetime.utcnow().isoformat()
            }
        chat.messages.append(new_message)
        await chat.save()

        return DealsOut(
            uuid=deal.uuid,
            ad_uuid=deal.ad_uuid.uuid,
            buyer_id=deal.buyer_id.uuid,
            seller_id=deal.seller_id.uuid,
            status=deal.status,
            price=deal.price,
            currency=deal.currency,
            is_frozen=deal.is_frozen,
            support_request=deal.support_request,
            created_at=deal.created_at,
            updated_at=deal.updated_at
        )

    @staticmethod
    async def get_user_deals(user_id: int, status: DealStatus = None) -> List[DealsOut]:
        user = await UserController.get_by_tg_id(user_id)
        query = Deals.filter(Q(buyer_id=user) | Q(seller_id=user)).prefetch_related("ad_uuid", "buyer_id", "seller_id")

        if status:
            query = query.filter(status=status)

        deals = await query
        result = []
        for deal in deals:
            result.append(DealsOut(
                uuid=deal.uuid,
                ad_uuid=deal.ad_uuid.uuid,
                buyer_id=deal.buyer_id.uuid,
                seller_id=deal.seller_id.uuid,
                status=deal.status,
                price=deal.price,
                currency=deal.currency,
                is_frozen=deal.is_frozen,
                support_request=deal.support_request,
                created_at=deal.created_at,
                updated_at=deal.updated_at
            ))

        return result
    
    @staticmethod
    async def get_deal(user_id: int, status: DealStatus = None) -> List[DealOut]:
        user = await UserController.get_by_tg_id(user_id)
        query = Deals.filter(Q(buyer_id=user) | Q(seller_id=user)).prefetch_related("ad_uuid", "buyer_id", "seller_id")
        
        if status:
            query = query.filter(status=status)

        deals = await query
        result = []
        for deal in deals:
            result.append(DealOut(
                uuid=deal.uuid,
                ad_uuid=deal.ad_uuid.uuid,
                buyer_id=deal.buyer_id.uuid,
                seller_id=deal.seller_id.uuid,
                status=deal.status,
                price=deal.price,
                currency=deal.currency,
                is_frozen=deal.is_frozen,
                support_request=deal.support_request,
                created_at=deal.created_at,
                updated_at=deal.updated_at
            ))

        return result


    """
    ----------- CHATS -----------
    """

    @staticmethod
    async def send_chat_message(deal_uuid: UUID, message_data: ChatMessageCreate, sender) -> ChatMessage:
        deal = await Deals.get(uuid=deal_uuid).prefetch_related("buyer_id", "seller_id")
        if sender.uuid not in [deal.buyer_id.uuid, deal.seller_id.uuid]:
            raise APIException(error="Access denied", status_code=403)
        
        timestamp = datetime.now(timezone.utc).isoformat()
        chat = await Chats.get(deal=deal)

        new_message = {
            "sender_name": sender.username,
            "sender_tg_id": sender.tg_id,
            "sender_uuid": str(sender.uuid),
            "text": message_data.text,
            "timestamp": timestamp
        }
        chat.messages.append(new_message)
        await chat.save()
        
        return ChatMessage(**new_message)

    @staticmethod
    async def update_chat_pin(chat_uuid: str, is_pinned: bool):
        try:
            chat = await Chats.get(uuid=chat_uuid).prefetch_related('deal')
            chat.is_pinned = is_pinned
            await chat.save()
            return chat
        
        except DoesNotExist:
            raise APIException(status_code=404, error="Deal not found")
        except Exception as e:
            raise APIException(status_code=400, error=str(e))
        
    @staticmethod
    async def get_deal_chat(deal_uuid: UUID, user_id: int) -> ChatOut:
        deal = await Deals.get(uuid=deal_uuid).prefetch_related("buyer_id", "seller_id")
        user = await UserController.get_by_tg_id(user_id)

        if user.uuid not in [deal.buyer_id.uuid, deal.seller_id.uuid]:
            raise APIException(error="Access denied", status_code=403)
        
        chat = await Chats.filter(deal=deal).select_related("deal__buyer_id", "deal__seller_id").get()
        return chat

    @staticmethod
    async def get_all_user_chats(user_id: int) -> List[ChatAllOut]:
        try:
            user = await UserController.get_by_tg_id(user_id)
            deals = await Deals.filter(
                Q(buyer_id=user) | Q(seller_id=user)
            ).prefetch_related("seller_id", "buyer_id", "chat")
            
            result = []
            for deal in deals:
                chat = await deal.chat
                is_seller = user.uuid == deal.seller_id.uuid
                counterpart = deal.buyer_id if is_seller else deal.seller_id
                
                result.append(
                    ChatAllOut(
                        uuid=chat.uuid,
                        deal_uuid=deal.uuid,
                        is_pinned=chat.is_pinned,
                        counterpart_id=counterpart.uuid,
                        counterpart_isvip=counterpart.is_vip,
                        counterpart_photo=counterpart.profile_photo or "",
                        counterpart_username=counterpart.username or "",
                        user_role="seller" if is_seller else "buyer"
                    )
                )
            return result
        except DoesNotExist:
            raise APIException(status_code=404, error="User not found")
        except Exception as e:
            raise APIException(status_code=400, error=str(e))