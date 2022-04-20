import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sort import Base


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
