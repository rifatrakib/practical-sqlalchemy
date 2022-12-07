from sqlalchemy.orm import registry, Session, declarative_base, relationship
from sqlalchemy import (
    Table, Column, Integer, String, ForeignKey, inspect, create_engine, select
)

Base = declarative_base()


class DeclarativeUser(Base):
    __tablename__ = "declarative_user"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    
    addresses = relationship("Address", back_populates="user")


class Address(Base):
    __tablename__ = "address"
    
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("declarative_user.id"))
    
    user = relationship("DeclarativeUser", back_populates="addresses")


u1 = DeclarativeUser(name="some name", fullname="some fullname")

mapper_registry = registry()

imperative_user_table = Table(
    "imperative_user",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
)


class ImperativeUser:
    pass


mapper_registry.map_imperatively(ImperativeUser, imperative_user_table)

mapper = DeclarativeUser.__mapper__
print(f"{mapper = }")

mapper = inspect(DeclarativeUser)
print(f"{mapper = }")

table = DeclarativeUser.__table__
print(f"{table = }")

table = inspect(DeclarativeUser).local_table
print(f"{table = }")

table = inspect(DeclarativeUser).selectable
print(f"{table = }")

insp = inspect(DeclarativeUser)
print(f"{insp = }")
print(f"{insp.columns = }")
print(f"{list(insp.columns) = }")
print(f"{insp.columns.name = }")
print(f"{insp.all_orm_descriptors = }")
print(f"{insp.all_orm_descriptors.keys() = }")
print(f"{list(insp.column_attrs) = }")
print(f"{insp.column_attrs.name = }")
print(f"{insp.column_attrs.name.expression = }")

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
session = Session(engine)

Base.metadata.create_all(engine)

sandy = DeclarativeUser(name="sandy", fullname="Sandy Cheeks")
patrick = DeclarativeUser(name="patrick", fullname="Patrick Star")
squidward = DeclarativeUser(name="squidward", fullname="Squidward Tentacles")
krabs = DeclarativeUser(name="ehkrabs", fullname="Eugene H. Krabs")

session.add_all([sandy, patrick, squidward, krabs])
session.commit()

u1 = session.scalars(select(DeclarativeUser)).first()
print(f"{u1.name = }")

insp = inspect(u1)
print(f"{insp = }")
print(f"{insp.mapper = }")
print(f"{insp.session = }")
print(f"{insp.persistent = }")
print(f"{insp.pending = }")
print(f"{insp.unmodified = }")

print(f"{insp.attrs.fullname.value = }")

u1.fullname = "New fullname"
print(f"{insp.attrs.fullname.history = }")
