import uuid

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List

from back.auth.auth import get_user
from back.errors import APIException, APIExceptionModel
from back.models.enums import Categories
from back.views.ads import AdCreate, AdOut, DealCreate, DealOut, AdCreateOut, ChatOut
from back.views.auth.user import AuthUserOut
from back.controllers.user import UserController
from back.controllers.orders import OrderController


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
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/ads", 
    response_model=List[AdOut]
)
async def get_ads(category: Categories = Query(None)):
    ads = await OrderController.get_ads(category=category)
    return ads


@router.get(
    "/ads/{ad_uuid}", 
    response_model=AdOut
)
async def get_ad(ad_uuid: uuid.UUID):
    try:
        ad = await OrderController.get_ad(ad_uuid=ad_uuid)
        return ad
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/deals", 
    response_model=DealOut, 
    responses={400: {"model": APIExceptionModel}}, 
)
async def create_deal(
    deal_data: DealCreate, 
    user_id: int = Depends(UserController.get_by_tg_id)
):
    try:
        deal = await OrderController.create_deal(user_id=user_id, deal_data=deal_data)
        return deal
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/deals", 
    response_model=List[DealOut]
)
async def get_user_deals(user_id: int = Depends(UserController.get_by_tg_id)):
    try:
        deals = await OrderController.get_user_deals(user_id=user_id)
        return deals
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/deals/{deal_uuid}", response_model=DealOut)
async def get_deal(deal_uuid: uuid.UUID, user_id: int = Depends(UserController.get_by_tg_id)):
    try:
        deal = await OrderController.get_deal(deal_uuid=deal_uuid, user_id=user_id)
        return deal
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@router.post(
    "/deals/{deal_uuid}/confirm", 
    response_model=DealOut,
    responses={400: {"model": APIExceptionModel}}, 
)
async def confirm_deal(
    deal_uuid: uuid.UUID,
    user: AuthUserOut = Depends(get_user)
):
    try:
        deal = await OrderController.confirm_deal(
            deal_uuid=str(deal_uuid),
            tg_id=user.tg_id
        )
        return deal
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))

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
            tg_id=user.tg_id
        )
        return chat
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))