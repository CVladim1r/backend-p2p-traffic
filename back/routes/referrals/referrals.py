import logging

from decimal import Decimal
from fastapi import APIRouter, Depends

from tortoise.expressions import Q
from tortoise.functions import Sum, Count

from back.auth.auth import get_user
from back.views.auth import AuthUserOut
from back.models import Referrals, Deals
from back.models.enums import DealStatus
from back.controllers.user import UserController
from back.views.referrals import ReferralStatsOut, ReferralUserStats
from back.errors import APIExceptionModel, APIException

router = APIRouter()


@router.get(
    "/referrals",
    response_model=ReferralStatsOut,
    responses={401: {"model": APIExceptionModel}}
)
async def get_referrals_stats(
    user_in: AuthUserOut = Depends(get_user)
) -> ReferralStatsOut:
    try:
        user = await UserController.get_by_tg_id(user_in.tg_id)
        if not user:
            raise APIException("User not found", 404)

        referrals = await Referrals.filter(referrer=user).prefetch_related("referred")

        stats = []
        for ref in referrals:
            referred_user = ref.referred
            
            buys_stats = await Deals.filter(
                buyer=referred_user,
                status=DealStatus.COMPLETED
            ).annotate(
                total_amount=Sum('price'),
                deal_count=Count('uuid')
            ).values('total_amount', 'deal_count')

            sales_stats = await Deals.filter(
                seller=referred_user,
                status=DealStatus.COMPLETED
            ).annotate(
                total_amount=Sum('price'),
                deal_count=Count('uuid')
            ).values('total_amount', 'deal_count')


            deals_as_buyer = await Deals.filter(
                buyer=referred_user,
                status=DealStatus.COMPLETED
            ).prefetch_related("ad_uuid")
            
            total_earned = Decimal(0)
            for deal in deals_as_buyer:
                commission = deal.price - deal.ad_uuid.price
                total_earned += commission * Decimal('0.4')

            # deals_stats = await Deals.filter(
            #     Q(buyer=referred_user) | Q(seller=referred_user),
            #     status=DealStatus.COMPLETED
            # ).annotate(
            #     buy_amount=Sum('price', _filter=Q(buyer=referred_user)),
            #     buy_count=Count('uuid', _filter=Q(buyer=referred_user)),
            #     sale_amount=Sum('price', _filter=Q(seller=referred_user)),
            #     sale_count=Count('uuid', _filter=Q(seller=referred_user))
            # ).values('buy_amount', 'buy_count', 'sale_amount', 'sale_count')

            # stats_data = deals_stats[0] if deals_stats else {}


            stats.append(ReferralUserStats(
                uuid=str(referred_user.uuid),
                username=referred_user.username,
                profile_photo=referred_user.profile_photo,
                rating=float(referred_user.rating) if referred_user.rating else None,
                is_vip=referred_user.is_vip,
                completed_buys_count=buys_stats[0]['deal_count'] if buys_stats else 0,
                total_buys_amount=buys_stats[0]['total_amount'] if buys_stats else Decimal(0),
                completed_sales_count=sales_stats[0]['deal_count'] if sales_stats else 0,
                total_sales_amount=sales_stats[0]['total_amount'] if sales_stats else Decimal(0),
                total_earned=total_earned
            ))

        return ReferralStatsOut(referrals=stats)
    
    except Exception as error:
        logging.error(f"Error getting referrals: {error}")
        raise APIException("Failed to get referral stats", 500)