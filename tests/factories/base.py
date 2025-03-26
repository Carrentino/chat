from helpers.testing.async_factory import AsyncSQLAlchemyFactory

from tests.conftest import get_session


class BaseSqlAlchemyFactory(AsyncSQLAlchemyFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_factory = get_session
        sqlalchemy_session_persistence = 'commit'
