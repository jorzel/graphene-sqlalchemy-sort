from sqlalchemy import Column, Integer, MetaData, String, create_engine
from sqlalchemy.orm import configure_mappers, declarative_base

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
        return f"Example(id={self.id}, first_name={self.first_name}, second_name={self.second_name}"

    __repr__ = __str__


configure_mappers()
