from datetime import UTC, datetime, timedelta

import jwt
from config import setting
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

oauth_schema = OAuth2PasswordBearer(tokenUrl="api/users/token")


def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)


def verify_password(plain_password, hash_password) -> bool:
    return password_hash.verify(plain_password, hash_password)


def create_jwt_token(data: dict, expire_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now(UTC) - expire_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=setting.expire_token_in_mins,
        )
    to_encode.update({"epx": expire})

    token = jwt.encode(data, setting.sercet_key.get_secret_value(), setting.algorithm)
    return token


def verify_jwt_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, setting.sercet_key.get_secret_value())
        print("payload", payload)
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")
