import logging

from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, Depends, Body, Query
from tortoise.transactions import in_transaction
from dateutil.relativedelta import relativedelta, MO

from back.auth.auth import get_user
from back.models import UserBalance, VIPStatuses
from back.models.enums import TransactionCurrencyType
from back.errors import APIException, APIExceptionModel
from back.views.auth.user import AuthUserOut
from back.views.user.user import StartUserIn, StartUserOut, UserData, UserMainPageOut
from back.controllers.user import UserController
from back.controllers.balance import BalanceController

router = APIRouter()

@router.post(
    "/create_user",
    response_model=StartUserOut,
    responses={400: {"model": APIExceptionModel}},
)
async def create_user(
    user_data: StartUserIn = Body(...),
    user_in: AuthUserOut = Depends(get_user),
) -> StartUserOut:
    logging.info(f"Incoming create_user request: {user_data.dict()}")
    logging.info(f"User tg_id: {user_in.tg_id}")

    if user_in.tg_id != user_data.tg_id:
        logging.error(f"User mismatch: expected {user_in.tg_id}, got {user_data.tg_id}")
        raise APIException("User not match", 401)

    try:
        user = await UserController.add_user_if_not_exists(user_data.tg_id, user_data.username)
        return StartUserOut.model_validate(user)
    except Exception as error:
        logging.error(f"Error creating user {user_data.tg_id}, {user_data.username}: {error}")
        raise APIException(f"Create user failed: {error}", 400)

@router.get(
    "/main_data",
    response_model=UserMainPageOut,
    responses={400: {"model": APIExceptionModel}},
)
async def get_user_main_data(
    user_in: AuthUserOut = Depends(get_user),
) -> UserMainPageOut:
    
    logging.info(f"Incoming get_user_main_data request for tg_id: {user_in.tg_id}")

    user = await UserController.get_main_page_user_data(user_in.tg_id)
    if not user:
        raise APIException(f"User with tg_id {user_in.tg_id} not found", 404)

    balances = await UserBalance.filter(user=user).all()
    balance_data = {balance.currency: float(balance.balance) for balance in balances}

    balances = await UserBalance.filter(user=user).all()
    balance_data = {balance.currency: float(balance.balance) for balance in balances}

    roulette_last_spin_str = (
        user.roulette_last_spin.isoformat() 
        if isinstance(user.roulette_last_spin, datetime) 
        else user.roulette_last_spin
    )

    response = UserMainPageOut(
        uuid=user.uuid,
        tg_id=user.tg_id,
        username=user.username,
        rating=user.rating or 0.0,
        balance=balance_data,
        total_sales=user.total_sales,
        deals=0,
        roulette_last_spin=roulette_last_spin_str,
        referral_id=None,
        is_vip=user.is_vip,
        profile_photo=user.profile_photo,
        created_at=user.created_at.isoformat(),
        updated_at=user.update_at.isoformat() if user.update_at else user.created_at.isoformat(),
        )
    
    return response

@router.get(
    "/get_user_data",
    response_model=UserData,
    responses={400: {"model": APIExceptionModel}},
)
async def get_user_data(
    user_tg_id: int,
) -> UserData:
    user = await UserController.get_by_tg_id(user_tg_id)

    response = UserData(
        tg_id=user.tg_id,
        username=user.username,
        rating=user.rating or 0.0,
        total_sales=user.total_sales,
        deals=0,
        is_vip=user.is_vip,
        profile_photo=user.profile_photo,
        )
    
    return response

@router.post(
    "/update_user_photo",
    responses={400: {"model": APIExceptionModel}},
)
async def update_user_photo(
    user_in: AuthUserOut = Depends(get_user),
    photo_url: str = Body(..., embed=True),
):
    user = await UserController.get_main_page_user_data(user_in.tg_id)
    if not user:
        raise APIException(f"User with tg_id {user_in.tg_id} not found", 404)

    user.profile_photo = photo_url
    await user.save()

    return photo_url

@router.post(
    "/update_user_vip",
    responses={
        400: {"model": APIExceptionModel},
        404: {"model": APIExceptionModel},
    },
)
async def update_user_vip(
    user_in: AuthUserOut = Depends(get_user),
    currently_type: TransactionCurrencyType = Query(None),
):
    async with in_transaction():
        user = await UserController.get_by_tg_id(user_in.tg_id)
        if not user:
            raise APIException(f"User with tg_id {user_in.tg_id} not found", 404)

        current_time = datetime.now()
        
        active_vip = await VIPStatuses.filter(
            user_id=user.uuid,
            valid_until__gte=current_time
        ).first()
        if active_vip:
            raise APIException("User already has an active VIP status", 400)
        
        if currently_type == TransactionCurrencyType.TON:
            ton_balance, _ = await UserBalance.get_or_create(
                user=user,
                currency=TransactionCurrencyType.TON,
                defaults={"balance": Decimal("0.0"), "reserved": Decimal("0.0")}
            )
            if ton_balance.balance >= Decimal("10"):
                currency = TransactionCurrencyType.TON
                amount = Decimal("10")
        else:
            usdt_balance, _ = await UserBalance.get_or_create(
                user=user,
                currency=TransactionCurrencyType.USDT,
                defaults={"balance": Decimal("0.0"), "reserved": Decimal("0.0")}
            )
            if usdt_balance.balance >= Decimal("30"):
                currency = TransactionCurrencyType.USDT
                amount = Decimal("30")

        await BalanceController.update_balance(
            user_id=user.tg_id,
            currency=currency,
            amount=-amount
        )

        existing_vip = await VIPStatuses.filter(user_id=user.uuid).order_by("-valid_until").first()
        
        if existing_vip:
            new_valid_until = (
                existing_vip.valid_until + relativedelta(months=1)
                if existing_vip.valid_until > current_time
                else current_time + relativedelta(months=1)
            )
            existing_vip.valid_until = new_valid_until
            await existing_vip.save()
        else:
            await VIPStatuses.create(
                user_id=user,
                valid_until=current_time + relativedelta(months=1)
            )

        user.is_vip = True
        await user.save()

    return "Done"