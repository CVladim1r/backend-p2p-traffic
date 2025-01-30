from typing import Any, Dict, List
from decimal import Decimal

from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from back.controllers.base import BaseUserController, T
from back.controllers.user import UserController
from back.errors import APIExceptionModel, APIException
from back.models import Ads, Deals, Transactions, Users
from back.models.enums import AdStatus, DealStatus
from back.utils.cryptobot import crypto_service

import logging


class OrderController(BaseUserController):
    
    @staticmethod
    async def calculate_commission(price: Decimal) -> Decimal:
        rates = await crypto_service.get_exchange_rates()
        ton_rate = next(r for r in rates if r.source == "TON" and r.target == "USD")
        return (price * Decimal('0.10')) / Decimal(ton_rate.rate)
    

    @staticmethod
    async def create_ad(ad_data: Dict[str, Any], user_in) -> Ads:
        user = await Users.get(tg_id=user_in.tg_id)
        if not user:
            raise APIException(detail="User not found", status_code=404)

        ad = await Ads.create(
            user_id=user,
            category=ad_data.category,
            title=ad_data.title,
            description=ad_data.description,
            price=ad_data.price,
            guaranteed_traffic=ad_data.guaranteed_traffic,
            minimum_traffic=ad_data.minimum_traffic,
            conditions=ad_data.conditions,
            execution_time=ad_data.execution_time,
            is_paid_promotion=ad_data.is_paid_promotion,
            status=AdStatus.ACTIVE,
        )
        return ad
    
    @staticmethod
    async def get_ads(category: str = None) -> List[Ads]:
        if category:
            ads = await Ads.filter(category=category).all()
        else:
            ads = await Ads.all()
        return ads

    @staticmethod
    async def get_ad(ad_uuid: str) -> Ads:
        try:
            ad = await Ads.get(uuid=ad_uuid)
        except DoesNotExist:
            raise APIException(detail="Ad not found", status_code=404)
        return ad

    @staticmethod
    async def create_deal(deal_data: Dict[str, Any], tg_id: int) -> Deals:
        user = await UserController.get_by_tg_id(tg_id)
        if not user:
            raise APIException(detail="User not found", status_code=404)

        try:
            ad = await Ads.get(uuid=deal_data["ad_uuid"])
        except DoesNotExist:
            raise APIException(detail="Ad not found", status_code=404)

        if ad.user_id == user.id:
            raise APIException(detail="You cannot buy your own ad", status_code=400)

        async with in_transaction() as transaction:
            deal = await Deals.create(
                ad_uuid=ad.uuid,
                buyer_id=user.id,
                seller_id=ad.user_id,
                status=DealStatus.PENDING,
            )
            # Пример транзакции для резервирования средств (если требуется)
            # await Transactions.create(..., using_db=transaction)

        return deal