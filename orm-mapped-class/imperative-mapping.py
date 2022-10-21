from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import registry, relationship

mapper_registry = registry()
Base = mapper_registry.generate_base()


class User:
    pass


class Address:
    pass


user_table = Table(
    "user",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("fullname", String(50)),
    Column("nickname", String(12)),
)

address = Table(
    "address",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("email_address", String(50)),
)

mapper_registry.map_imperatively(
    User,
    user_table,
    properties={
        "addresses": relationship(Address, backref="user", order_by=address.c.id)
    },
)

mapper_registry.map_imperatively(Address, address)
