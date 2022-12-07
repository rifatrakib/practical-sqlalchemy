from sqlalchemy import Column, MetaData, String, Table, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()
metadata = MetaData()

group_users = Table(
    "group_users",
    metadata,
    Column("user_id", String(40), nullable=False),
    Column("group_id", String(40), nullable=False),
    UniqueConstraint("user_id", "group_id"),
)


class GroupUsers(Base):
    __table__ = group_users
    __mapper_args__ = {"primary_key": [group_users.c.user_id, group_users.c.group_id]}
