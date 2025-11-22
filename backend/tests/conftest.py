import logging
from functools import lru_cache

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database  # type: ignore
from sqlalchemy_utils import database_exists

from main import app
from project.core.db.postgres.models import Base as BaseModel
from project.core.settings import settings

logger = logging.getLogger(__package__)


@pytest.fixture(scope="session", autouse=True)
def init_client():
    """Mocks infrastructure blocks for all tests."""
    client = TestClient(app=app, base_url="http://test")

    yield client


@pytest.fixture(scope="function")
def client(init_client):
    """Reset mocked infrastructure for each test function."""
    client = init_client

    yield client


@pytest.fixture(scope="session", autouse=True)
def init_db():
    """Creates test database in Postgres."""
    test_db = _get_test_db_url()
    engine = create_engine(test_db, future=True, echo=True)
    if not database_exists(test_db):
        create_database(test_db, template=settings.postgres_dbname)
        logger.info("Test DB created")
    else:
        logger.info("Use existed test DB")
    yield engine


@pytest.fixture(scope="function")
def db_engine(init_db):
    """Configures database tables and roll them back for each test.

    We don't use Session.rollback() because in tests we use both async (to create test data) and sync sessions
    (to assert changes in db) simultaneously. If we rollback async session (=transaction), then sync session will
    not see changes. So we recreate whole table's state for each test to allow async session commit changes as usual.
    """
    engine = init_db

    BaseModel.metadata.create_all(bind=engine)

    yield engine

    BaseModel.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def sync_session(db_engine):
    """Creates sync session to main db to assert some changes during tests."""
    connection = db_engine.connect()
    connection.begin()

    Session = sessionmaker(bind=connection)
    session = Session()
    logger.info("Tests use connection to db %s", session.connection().connection.driver_connection.dsn)

    yield session

    connection.close()


async def get_async_session():
    """Returns async session to test database inside async-test functions directly or in Depends()."""
    test_db = _get_test_db_url(sync=False)
    engine = create_async_engine(test_db, future=True, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        async with session.begin():
            yield session


@lru_cache(maxsize=2)
def _get_test_db_url(sync: bool = True) -> str:
    """Returns connection URL to testing database in sync or async mode."""
    if sync:
        test_db = settings.database_url.replace("+asyncpg", "")
    else:
        test_db = settings.database_url
    if not test_db.endswith("_test"):
        test_db = f"{test_db}_test"
    return test_db
