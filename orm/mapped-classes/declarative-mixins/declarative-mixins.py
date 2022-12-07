from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declared_attr, declarative_mixin, declarative_base

Base = declarative_base()


@declarative_mixin
class CustomMixin:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__
    
    __table_args__ = {"mysql_engine": "InnoDB"}
    __mapper_args__ = {"always_refresh": True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)


class UserModel(CustomMixin, Base):
    age = Column(Integer)
