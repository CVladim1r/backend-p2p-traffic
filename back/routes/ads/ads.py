import uuid

from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, Query

from back.auth.auth import get_user
from back.errors import APIException, APIExceptionModel
from back.models.enums import CategoriesAds, DealStatus
from back.models import Reviews, Deals
from back.views.auth.user import AuthUserOut
from back.controllers.user import UserController
from back.controllers.orders import OrderController
from back.views.ads import (
    AdOut,
    AdCreate,
    AdOutOne,
    AdCreateOut,
    DealCreate,
    DealOut,
    DealsOut,
    DealOutCOMPLETE,
    ChatOut,
    ChatPinOut,
    ChatAllOut,
    ChatMessage,
    ChatMessageCreate,
    PinChatRequest,
    ReviewOut,
    ReviewCreate
)

router = APIRouter()


@router.post(
    "/new_ad", 
    response_model=AdCreateOut, 
    responses={400: {"model": APIExceptionModel}}, 
)
async def create_ad(
    ad_data: AdCreate, 
    user_in: AuthUserOut = Depends(get_user),
) -> AdCreateOut:
    try:
        ad = await OrderController.create_ad(user_in=user_in, ad_data=ad_data)
        return AdCreateOut(uuid=ad.uuid, created_at=ad.created_at)
    except Exception as e:
        raise APIException(status_code=400, error=str(e))

@router.get(
    "/ads", 
    response_model=List[AdOut]
)
async def get_ads(category: CategoriesAds = Query(None)):
    ads = await OrderController.get_ads(category=category)
    return ads

@router.get(
    "/ads/{ad_uuid}", 
    response_model=AdOutOne
)
async def get_ad(
    ad_uuid: uuid.UUID
):
    try:
        ad = await OrderController.get_ad(ad_uuid=ad_uuid)

        price_plus_commision=ad.price* Decimal("0.1") + ad.price

        user = ad.user_id
        return AdOutOne(
            uuid=ad.uuid,
            category=ad.category,
            ad_type=ad.type_ads,
            title=ad.title,
            description=ad.description,
            price=round(price_plus_commision,3),
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
            user_rating=float(user.rating) if user.rating else 5.0,
            user_vip=user.is_vip,
        )
    except Exception as e:
        raise APIException(status_code=404, error=str(e))

@router.post(
    "/deals", 
    response_model=DealsOut, 
    responses={400: {"model": APIExceptionModel}}, 
)
async def create_deal(
    deal_data: DealCreate, 
    user_in: AuthUserOut = Depends(get_user),
):
    try:
        deal = await OrderController.create_deal(
            user_id=user_in.tg_id, 
            deal_data=deal_data
        )
        return deal
    except APIException as e:
        raise APIException(status_code=400, error=str(e))

@router.get(
    "/deals", 
    response_model=List[DealsOut]
)
async def get_user_deals(
    user_in: AuthUserOut = Depends(get_user),
):
    try:
        deals = await OrderController.get_user_deals(user_id=user_in.tg_id)
        return deals
    except Exception as e:
        raise APIException(status_code=400, error=str(e))

@router.get(
    "/deals/{deal_uuid}", 
    response_model=DealOut
)
async def get_deal(
    deal_uuid: uuid.UUID, 
):
    try:
        deal = await OrderController.get_deal(deal_uuid=deal_uuid)
        return deal
    except Exception as e:
        raise APIException(status_code=404, error=str(e))
    
@router.post(
    "/deals/{deal_uuid}/confirm", 
    response_model=DealOutCOMPLETE,
    responses={400: {"model": APIExceptionModel}}, 
)
async def confirm_deal(
    deal_uuid: uuid.UUID,
    user: AuthUserOut = Depends(get_user)
):
    deal = await OrderController.confirm_deal(
        deal_uuid=deal_uuid,
        user_id=user.tg_id
    )
    return deal

@router.get(
    "/deals/{deal_uuid}/chat",
    response_model=ChatOut,
    responses={403: {"description": "Forbidden"}}
)
async def get_chat(
    deal_uuid: uuid.UUID,
    user: AuthUserOut = Depends(get_user)
):
    try:
        chat = await OrderController.get_deal_chat(
            deal_uuid=str(deal_uuid),
            user_id=user.tg_id
        )
        return chat
    except APIException as e:
        raise APIException(status_code=400, error=str(e))
    
@router.post(
    "/deals/{deal_uuid}/chat/messages",
    response_model=ChatMessage,
    responses={403: {"description": "Forbidden"}}
)
async def send_chat_message(
    deal_uuid: uuid.UUID,
    message_data: ChatMessageCreate,
    user_in: AuthUserOut = Depends(get_user)
):
    user = await UserController.get_by_tg_id(user_in.tg_id)
    try:
        message = await OrderController.send_chat_message(
            deal_uuid=deal_uuid,
            message_data=message_data,
            sender=user
        )
        return message
    except APIException as e:
        raise APIException(status_code=400, error=str(e))
    
@router.patch(
    "/deals/{chat_uuid}/chat/pin",
    response_model=ChatPinOut,
    responses={
        403: {"model": APIExceptionModel},
        404: {"model": APIExceptionModel}
    }
)
async def pin_chat(
    chat_uuid: uuid.UUID,
    pin_data: PinChatRequest,
    user: AuthUserOut = Depends(get_user)
):
    try:
        chat = await OrderController.update_chat_pin(
            chat_uuid=str(chat_uuid),
            is_pinned=pin_data.is_pinned,
        )
        return chat
    except APIException as e:
        raise APIException(status_code=400, error=str(e))
    except Exception as e:
        raise APIException(status_code=400, error=str(e))
    
@router.get(
    "/chats",
    response_model=List[ChatAllOut],
    responses={403: {"model": APIExceptionModel}}
)
async def get_all_chats(
    user: AuthUserOut = Depends(get_user)
):
    try:
        chats = await OrderController.get_all_user_chats(user_id=user.tg_id)
        return chats
    except APIException as e:
        raise APIException(status_code=e.status_code, error=str(e.error))

@router.post(
    "/deals/{deal_uuid}/reviews",
    response_model=ReviewOut,
    responses={
        400: {"model": APIExceptionModel},
        404: {"model": APIExceptionModel}
    }
)
async def create_review(
    deal_uuid: uuid.UUID,
    review_data: ReviewCreate,
    user_in: AuthUserOut = Depends(get_user)
):
    try:
        deal = await Deals.get(uuid=deal_uuid).prefetch_related(
            "buyer_id", "seller_id", "ad_uuid"
        )
        if deal.status != DealStatus.COMPLETED:
            raise APIException("Отзывы можно оставлять только для завершенных сделок", 400)

        user = await UserController.get_by_tg_id(user_in.tg_id)
        if user.uuid not in [deal.buyer_id.uuid, deal.seller_id.uuid]:
            raise APIException("Пользователь не участвовал в сделке", 403)

        if user.uuid == deal.buyer_id.uuid:
            reviewed_user = deal.seller_id
        else:
            reviewed_user = deal.buyer_id

        existing_review = await Reviews.exists(
            deal_uuid=deal,
            reviewer_id=user
        )
        if existing_review:
            raise APIException("Вы уже оставили отзыв по этой сделке", 400)

        new_review = await Reviews.create(
            deal_uuid=deal,
            reviewer_id=user,
            reviewed_user_id=reviewed_user,
            rating=review_data.rating,
            comment=review_data.comment
        )

        if user.uuid == deal.buyer_id.uuid:
            if deal.buyer_review:
                raise APIException(
                    error="Buyer already review the deal",
                    status_code=400
                )
            deal.buyer_review = True
        else:
            if deal.seller_review:
                raise APIException(
                    error="Seller already review the deal",
                    status_code=400
                )
            deal.seller_review = True


        await new_review.fetch_related(
            "deal_uuid", 
            "reviewer_id", 
            "reviewed_user_id"
        )

        return ReviewOut(
            uuid=new_review.uuid,
            deal_uuid=new_review.deal_uuid.uuid,
            reviewer_id=new_review.reviewer_id.uuid,
            reviewed_user_id=new_review.reviewed_user_id.uuid,
            rating=new_review.rating,
            comment=new_review.comment,
            created_at=new_review.created_at.isoformat(),
            seller_review=new_review.deal_uuid.seller_review,
            buyer_review=new_review.deal_uuid.buyer_review,
            # buyer_review=deal.
            # seller_review=deal.seller_review
        )
    except APIException as e:
        raise e
    except Exception as e:
        raise APIException(str(e), 500)