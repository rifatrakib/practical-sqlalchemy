from sqlalchemy import Column, Integer, String, Table, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import DeferredReflection

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
Base = declarative_base()


class UserInline(Base):
    __table__ = Table(
        "user",
        Base.metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("fullname", String),
        Column("nickname", String),
    )


Base.metadata.create_all(engine)


class User(Base):
    __table__ = Table(
        "user",
        Base.metadata,
        autoload_with=engine,
    )


Base.metadata.reflect(engine)


class ReflectedUser(Base):
    __table__ = Base.metadata.tables["user"]


class FooBase(Base):
    __table__ = Table(
        "foo",
        Base.metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("fullname", String),
        Column("nickname", String),
    )


class BarBase(Base):
    __table__ = Table(
        "bar",
        Base.metadata,
        Column("id", Integer, primary_key=True),
        Column("foo_id", ForeignKey("foo.id")),
    )


Base.metadata.create_all(engine)


class Reflected(DeferredReflection):
    __abstract__ = True


class Foo(Reflected, Base):
    __tablename__ = "foo"


class Bar(Reflected, Base):
    __tablename__ = "bar"


Reflected.prepare(engine)
