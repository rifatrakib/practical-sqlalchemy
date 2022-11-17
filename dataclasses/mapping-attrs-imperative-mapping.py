from __future__ import annotations
from typing import List, Optional
from attrs import define
from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table
from sqlalchemy.orm import registry, relationship

mapper_registry = registry()
metadata_obj = MetaData()


@define(slots=False)
class User:
    id: int
    name: str
    fullname: str
    nickname: str
    addresses: List[Address]


@define(slots=False)
class Address:
    id: int
    user_id: int
    email_address: Optional[str]


user = Table(
    "user",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("fullname", String(50)),
    Column("nickname", String(12)),
)

address = Table(
    "address",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("email_address", String(50)),
)

mapper_registry.map_imperatively(
    User, user, properties={
        "addresses": relationship(Address, backref="user", order_by=address.c.id),
    },
)

mapper_registry.map_imperatively(Address, address)
