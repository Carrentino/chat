import contextlib
from functools import lru_cache

from helpers.api.middleware.auth.constants import DEFAULT_ALGORITHM
from helpers.contextvars import USER_CTX
from helpers.errors.auth import InvalidTokenError
from helpers.jwt import decode_jwt
from helpers.models.user import UserContext
from helpers.sqlalchemy.client import SQLAlchemyClient
from jose import JOSEError
from pydantic import ValidationError, PostgresDsn
from starlette.websockets import WebSocket

from src.settings import get_settings


def get_user(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        raise InvalidTokenError

    with contextlib.suppress(JOSEError):
        payload = decode_jwt(token, get_settings().jwt_key.get_secret_value(), DEFAULT_ALGORITHM)
    if not payload:
        raise InvalidTokenError

    try:
        user_model = UserContext.model_validate(payload)
    except ValidationError as err:
        raise InvalidTokenError from err

    USER_CTX.set(user_model)
    return user_model


@lru_cache
def make_db_client(dsn: PostgresDsn = get_settings().postgres_dsn) -> SQLAlchemyClient:
    return SQLAlchemyClient(dsn=dsn)
