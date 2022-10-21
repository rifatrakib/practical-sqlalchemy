from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import registry


mapper_registry = registry()

user_table = Table(
    "user",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("fullname", String(50)),
    Column("nickname", String(12)),
)


class User:
    pass


mapper_registry.map_imperatively(User, user_table)
