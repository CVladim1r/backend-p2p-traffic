from uuid import uuid4
import uuid
from typing import List
from fastapi import APIRouter, Depends, Query

from back.auth.auth import get_user
from back.errors import APIException, APIExceptionModel
from back.models.enums import CategoriesAds
from back.views.auth.user import AuthUserOut
from back.controllers.user import UserController
from back.controllers.orders import OrderController
from back.views.ads import (
    AdOut,
    AdCreate,
    AdOutOne,
    AdCreateOut,
    DealCreate,
    DealsOut,
    DealOutCOMPLETE,
    ChatOut,
    ChatPinOut,
    ChatAllOut,
    ChatMessage,
    ChatMessageCreate,
    PinChatRequest
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

        user = ad.user_id
        return AdOutOne(
            uuid=ad.uuid,
            category=ad.category,
            ad_type=ad.type_ads,
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

# @router.get(
#     "/deals/{deal_uuid}", 
#     response_model=DealsOut
# )
# async def get_deal(
#     deal_uuid: uuid.UUID, 
# ):
#     try:
#         deal = await OrderController.get_deal(deal_uuid=deal_uuid)
#         return deal
#     except Exception as e:
#         raise HTTPException(status_code=404, detail=str(e))
    
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