import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base, Example, Item


@pytest.fixture(scope="session")
def db_connection():
    SQLALCHEMY_DATABASE_URL = "sqlite:///"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    connection = engine.connect()

    yield connection

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(db_connection):
    transaction = db_connection.begin()
    session = sessionmaker(bind=db_connection)
    db_session = session()

    yield db_session

    transaction.rollback()
    db_session.close()


@pytest.fixture
def example_factory(db_session):
    def _example_factory(**kwargs):
        example = Example(**kwargs)
        db_session.add(example)
        db_session.flush()
        return example

    yield _example_factory


@pytest.fixture
def item_factory(db_session):
    def _item_factory(**kwargs):
        item = Item(**kwargs)
        db_session.add(item)
        db_session.flush()
        return item

    yield _item_factory
