import logging

import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from sqlalchemy import Column, Integer, MetaData, String, create_engine
from sqlalchemy.orm import configure_mappers, declarative_base

# logging config
LOGGER_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(format=LOGGER_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# db config
DB_URI = "sqlite:///:memory:"
engine = create_engine(DB_URI)
metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Example(Base):
    __tablename__ = "example"

    id = Column(Integer, primary_key=True, autoincrement=True)
    counter = Column(Integer, default=0, nullable=False)
    first_name = Column(String)
    second_name = Column(String)

    def __str__(self):
        return f"Example(id={self.id}, important_counter={self.important_counter}"

    __repr__ = __str__


configure_mappers()


class ExampleNode(SQLAlchemyObjectType):
    class Meta:
        model = Example
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    examples = SQLAlchemyConnectionField(ExampleNode)


schema = graphene.Schema(query=Query)
