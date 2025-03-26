import asyncio
import sys
from asyncio import AbstractEventLoop
from collections.abc import AsyncGenerator, Generator
from functools import lru_cache
from typing import Any

import pytest
from fastapi import FastAPI
from helpers.depends.db_session import get_db_client
from helpers.sqlalchemy.client import SQLAlchemyClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.bootstrap import make_app
from src.settings import get_settings, Settings
from tests.constants import TEST_AUTH_TOKEN

TEST_SQL_ALCHEMY_CLIENT = SQLAlchemyClient(dsn=get_settings().test_postgres_dsn)


@lru_cache
def get_client() -> SQLAlchemyClient:
    return SQLAlchemyClient(dsn=get_settings().test_postgres_dsn)


def get_session() -> AsyncSession:
    return get_client().get_session()


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items: Any) -> None:
    for item in items:
        item.add_marker(pytest.mark.anyio)


@pytest.fixture(scope='session', autouse=True)
def anyio_backend() -> str:
    return 'asyncio'


@pytest.fixture(scope='session', autouse=True)
def event_loop() -> Generator[AbstractEventLoop, Any, None]:
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
async def setup_db() -> AsyncGenerator[SQLAlchemyClient, None]:
    client = TEST_SQL_ALCHEMY_CLIENT

    await client.drop_database(dsn=get_settings().test_postgres_dsn)
    await client.create_database(dsn=get_settings().test_postgres_dsn)
    await client.create_all_tables()

    yield client

    await client.close()


@pytest.fixture()
async def session() -> AsyncSession:
    return get_session()


@pytest.fixture(scope='session', autouse=True)
async def app() -> FastAPI:
    app = make_app()

    app.dependency_overrides[get_db_client] = get_client

    return app


@pytest.fixture()
async def settings() -> Settings:
    return get_settings()


@pytest.fixture()
async def client(
    app: FastAPI,
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client


@pytest.fixture()
async def auth_client(
    app: FastAPI,
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test', headers={'X-Auth-Token': TEST_AUTH_TOKEN}) as client:
        yield client
