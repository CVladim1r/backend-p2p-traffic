import logging
import uuid
import pytz

from fastapi import APIRouter, HTTPException
from datetime import datetime

from back.auth.token import create_token
from back.views.auth.auth import AuthIn, AuthOut
from back.models.user import User
router = APIRouter()


@router.post("", response_model=AuthOut)
async def post_auth(init_data: AuthIn):
    logging.info(init_data)

    payload = {
        "iss": uuid.uuid4().hex,
    }

    if init_data.init_ton:
        payload["address"] = init_data.init_ton.address
        payload["net"] = "testnet"

    if init_data.init_data_raw:
        payload["name"] = init_data.init_data_raw.user.username
        payload["lang"] = init_data.init_data_raw.user.language_code
        payload["sub"] = str(init_data.init_data_raw.user.id)

    access_token = create_token(payload)

    return AuthOut(access_token=access_token)
