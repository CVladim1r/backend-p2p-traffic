import datetime
import logging

from jose import JWTError, jwt

from back.errors import APIException


def load_jwt_key(filename: str):
    with open(filename) as key_file:
        return key_file.read()


def create_token(data):
    pk = load_jwt_key("security/api.pem")  # for local dev - ../security/api.pem'
    to_encode = data

    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=31)
    to_encode.update({"exp": expire})
    to_encode.update({"iat": datetime.datetime.now(datetime.timezone.utc)})
    try:
        encoded_jwt = jwt.encode(to_encode, pk, algorithm="RS256")
    except JWTError as e:
        logging.error(e)
        raise APIException(status_code=401, error="Wrong access token")
    return encoded_jwt
