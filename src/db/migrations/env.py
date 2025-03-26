import asyncio

from alembic import context
from helpers.sqlalchemy.base_model import Base
from helpers.sqlalchemy.client import SQLAlchemyClient
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.future import Connection

from src.db.models import load_all_models
from src.settings import Settings

settings = Settings(_env_file='.env')

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(SQLAlchemyClient(dsn=settings.postgres_dsn).create_database(dsn=settings.postgres_dsn))

load_all_models()
target_metadata = Base.metadata


async def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """

    dsn = settings.postgres_dsn
    context.configure(
        url=dsn.unicode_string().replace(dsn.scheme, 'postgresql'),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = create_async_engine(settings.postgres_dsn.unicode_string())
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


loop = asyncio.get_event_loop()
if context.is_offline_mode():
    task = run_migrations_offline()
else:
    task = run_migrations_online()

loop.run_until_complete(task)
