from sqlalchemy import Column, ForeignKey, Integer, String, Table, func, select
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# construct a Table directly
# the Base.metadata collection is usually a good choice
# for MetaData but any MetaData collection may be used
user_table = Table(
    "user",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("fullname", String),
    Column("nickname", String),
)


# construct the User class using this table.
class User(Base):
    __table__ = user_table


class UserInline(Base):
    __table__ = Table(
        "user_inline",
        Base.metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("fullname", String),
        Column("nickname", String),
    )


class Person(Base):
    __table__ = Table(
        "person",
        Base.metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(50)),
        Column("type", String(50)),
    )
    
    __mapper_args__ = {
        "polymorphic_on": __table__.c.type,
        "polymorphic_identity": "person",
    }
