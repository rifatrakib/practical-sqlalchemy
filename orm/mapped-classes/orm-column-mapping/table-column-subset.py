from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import declarative_base

Base = declarative_base()

user_table = Table(
    "user_table",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("user_name", String),
    Column("first_name", String),
    Column("last_name", String),
)

address_table = Table(
    "address_table",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user_table.id")),
    Column("street", String),
    Column("city", String),
    Column("state", String),
    Column("zip", String),
)


class User(Base):
    __table__ = user_table
    __mapper_args__ = {"include_properties": ["id", "user_name"]}


class Address(Base):
    __table__ = address_table
    __mapper_args__ = {"exclude_properties": ["street", "city", "state", "zip"]}


class UserAddress(Base):
    __table__ = user_table.join(address_table)
    __mapper_args__ = {
        "exclude_properties": [address_table.c.id],
        "primary_key": [user_table.c.id]
    }
