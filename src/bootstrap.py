from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Any

from fastapi import APIRouter, FastAPI
from fastapi.responses import UJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from helpers.api.bootstrap.setup_error_handlers import setup_error_handlers
from helpers.api.middleware.auth import AuthMiddleware
from helpers.api.middleware.trace_id.middleware import TraceIdMiddleware
from helpers.api.middleware.unexpected_errors.middleware import ErrorsHandlerMiddleware
from helpers.sqlalchemy.client import SQLAlchemyClient
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import PostgresDsn

from src.settings import get_settings
from src.web.api.chat.views import router as chat_router


@lru_cache
def make_db_client(dsn: PostgresDsn = get_settings().postgres_dsn) -> SQLAlchemyClient:
    return SQLAlchemyClient(dsn=dsn)


@asynccontextmanager
async def _lifespan(
    app: FastAPI,  # noqa
) -> AsyncGenerator[dict[str, Any], None]:
    client = make_db_client()

    yield {
        'db_client': client,
    }

    await client.close()


def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(ErrorsHandlerMiddleware, is_debug=get_settings().debug)  # type: ignore
    app.add_middleware(TraceIdMiddleware)  # type: ignore
    app.add_middleware(AuthMiddleware, key=get_settings().jwt_key)  # type: ignore


def setup_api_routers(app: FastAPI) -> None:
    api_router = APIRouter(prefix='/api')
    api_router.include_router(chat_router, prefix='/chat', tags=['chat'])
    app.include_router(router=api_router)


def setup_prometheus(app: FastAPI) -> None:
    Instrumentator(should_group_status_codes=False).instrument(app).expose(
        app, should_gzip=True, name='prometheus_metrics', endpoint='/metrics'
    )


def make_app() -> FastAPI:
    app = FastAPI(
        title='base',
        lifespan=_lifespan,
        docs_url='/api/docs',
        redoc_url='/api/redoc',
        openapi_url='/api/openapi.json',
        default_response_class=UJSONResponse,
    )

    setup_error_handlers(app, is_debug=get_settings().debug)
    setup_prometheus(app)
    setup_api_routers(app)
    setup_middlewares(app)

    return app
