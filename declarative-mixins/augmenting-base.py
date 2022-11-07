from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declared_attr, declarative_base


class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    __table_args__ = {"mysql_engine": "InnoDB"}
    
    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=Base)


class MyModel(Base):
    name = Column(String(1000))
