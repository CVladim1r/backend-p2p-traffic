import uuid

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from tortoise.exceptions import DoesNotExist
from typing import List

from back.models import Ads, Deals
from back.models.enums import Categories
from back.views.ads import AdCreate, AdOut, DealCreate, DealOut
from back.controllers.user import UserController
from back.controllers.orders import OrderController


router = APIRouter()

@router.post("/ads", response_model=AdOut, responses={400: {"description": "Bad Request"}})
async def create_ad(ad_data: AdCreate, user_id: int = Depends(UserController.get_by_tg_id)):
    try:
        ad = await OrderController.create_ad(user_id=user_id, ad_data=ad_data)
        return ad
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ads", response_model=List[AdOut])
async def get_ads(category: Categories = Query(None)):
    ads = await OrderController.get_ads(category=category)
    return ads


@router.get("/ads/{ad_uuid}", response_model=AdOut)
async def get_ad(ad_uuid: uuid.UUID):
    try:
        ad = await OrderController.get_ad(ad_uuid=ad_uuid)
        return ad
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/deals", response_model=DealOut, responses={400: {"description": "Bad Request"}})
async def create_deal(deal_data: DealCreate, user_id: int = Depends(UserController.get_by_tg_id)):
    try:
        deal = await OrderController.create_deal(user_id=user_id, deal_data=deal_data)
        return deal
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/deals", response_model=List[DealOut])
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