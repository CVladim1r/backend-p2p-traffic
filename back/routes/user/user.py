import logging
import uuid

from fastapi import APIRouter, Depends, Body

from back.auth.auth import get_user
from back.models.users import Users
from back.errors import APIException, APIExceptionModel
from back.auth.auth import JWTBearer
from back.views.auth.user import AuthUserOut
from back.views.user.user import StartUserIn, StartUserOut, UserMainPageIn, UserMainPageOut, UserOut
from back.controllers.user import UserController

router = APIRouter(dependencies=[Depends(JWTBearer())])

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

    logging.info(f"----------------")

    logging.info(f"Incoming create_user request: {user_data}")

    if user_in.tg_id != user_data.tg_id:
        raise APIException("User not match", 401)

    try:
        user = await UserController.add_user_if_not_exists(user_data.tg_id, user_data.username, user_data.is_premium)
        return StartUserOut.model_validate(user)
    except Exception as error:
        logging.error(f"Error creating user {user_data.tg_id}, {user_data.username}")
        raise APIException(f"Create user {error=}", 400)

