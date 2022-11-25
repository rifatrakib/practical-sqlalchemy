from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.orm import registry, declarative_base

Base = declarative_base()
mapper_registry = registry()


class User(Base):
    __tablename__ = "user"
    
    id = Column("user_id", Integer, primary_key=True)
    name = Column("user_name", String(50))


user_table = Table(
    "user_table",
    Base.metadata,
    Column("user_id", Integer, primary_key=True),
    Column("user_name", String),
)


class UserTable(Base):
    __table__ = user_table
    
    id = user_table.c.user_id
    name = user_table.c.user_name


class ImperativeUser:
    pass


imperative_user_table = Table(
    "imperative_user_table",
    mapper_registry.metadata,
    Column("user_id", Integer, primary_key=True),
    Column("user_name", String),
)

mapper_registry.map_imperatively(
    ImperativeUser,
    imperative_user_table,
    properties={
        "id": imperative_user_table.c.user_id,
        "name": imperative_user_table.c.user_name,
    }
)
