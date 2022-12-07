from __future__ import annotations
from typing import List, Optional
from attrs import define
from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table
from sqlalchemy.orm import registry, relationship

mapper_registry = registry()


@mapper_registry.mapped
@define(slots=False)
class User:
    __table__ = Table(
        "user",
        mapper_registry.metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(50)),
        Column("fullname", String(50)),
        Column("nickname", String(12)),
    )
    
    id: int
    name: str
    fullname: str
    nickname: str
    addresses: List[Address]
    
    __mapper_args__ = {"properties": {"addresses": relationship("Address")}}


@mapper_registry.mapped
@define(slots=False)
class Address:
    __table__ = Table(
        "address",
        mapper_registry.metadata,
        Column("id", Integer, primary_key=True),
        Column("user_id", Integer, ForeignKey("user.id")),
        Column("email_address", String(50)),
    )
    
    id: int
    user_id: int
    email_address: Optional[str]
