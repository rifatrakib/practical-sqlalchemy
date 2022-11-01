from sqlalchemy import Column, Integer, String, MetaData
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "some_schema"}
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)


metadata_obj = MetaData(schema="some_schema")
Base = declarative_base(metadata=metadata_obj)


class UserGlobal(Base):
    __tablename__ = "user_global"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)


UserGlobal.username = Column("username", String)
