import hashlib
import hmac
import logging
import os
from typing import Any

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from back.errors import APIException
from back.views.auth.auth import AuthIn
from back.views.auth.user import AuthUserOut

ALGORITHM = os.getenv("API_ALGORITHM", "RS256")


def load_jwt_key(filename: str):
    with open(filename) as key_file:
        return key_file.read()

pub_key = load_jwt_key("./security/api.crt")

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request, Authorization: str = Header()):  # Swagger Authorization doc
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise APIException(status_code=401, error="Invalid authentication scheme.")
            payload = self.verify_jwt(jwt_token=credentials.credentials)
            if not payload:
                raise APIException(status_code=401, error="Invalid token or expired token.")
            return payload
        else:
            raise APIException(status_code=401, error="Invalid authorization code.")

    @staticmethod
    def verify_jwt(jwt_token: str) -> dict[str, Any] | None:
        try:
            payload = jwt.decode(jwt_token, pub_key, algorithms=["RS256"])
        except Exception as e:
            logging.error(f"Error verify_jwt {e=}")
            payload = None

        return payload

def get_user(token_data=Depends(JWTBearer())) -> AuthUserOut:
    user = AuthUserOut.model_validate(
        {
            "name": token_data.get("name"),
            "tg_id": int(token_data["sub"]) if "sub" in token_data else None,
            "net": token_data.get("name"),
            "lang": token_data.get("lang"),
            "address": token_data.get("address"),
        }
    )
    return user

def telegram_validate(init_data: AuthIn):
    data_check_string = (
        f"auth_date={init_data.init_data_raw.auth_date}\n"
        f"query_id={init_data.init_data_raw.query_id}\n"
        f"user={init_data.init_data_raw.user.username}"
    )
    signature = hmac.new(str("").encode(), msg=data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()
    return signature
