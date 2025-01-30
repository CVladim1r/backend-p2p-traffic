import logging
import uuid

from fastapi import APIRouter, Depends, Body

from back.auth.auth import get_user
from back.models.users import UserBalance
from back.errors import APIException, APIExceptionModel
from back.views.auth.user import AuthUserOut
from back.views.user.user import StartUserIn, StartUserOut, UserMainPageIn, UserMainPageOut, UserOut
from back.controllers.user import UserController

router = APIRouter() # dependencies=[Depends(JWTBearer())]


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
        user = await UserController.add_user_if_not_exists(user_data.tg_id, user_data.username, user_data.is_premium)
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
    balance_data = {balance.currency: str(balance.balance) for balance in balances}

    response = UserMainPageOut(
        uuid=user.uuid,
        tg_id=user.tg_id,
        username=user.username,
        rating=user.rating or 0.0,
        balance=balance_data,
        total_sales=user.total_sales,
        deals=0,
        referral_id=None,
        is_vip=user.is_vip,
        profile_photo=user.profile_photo,
        created_at=user.created_at.isoformat(),
        updated_at=user.update_at.isoformat() if user.update_at else user.created_at.isoformat(),
        )
    
    return response

# TODO DELETE THIS SHIIIIIIIIIT
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

