from sqlalchemy import (
    MetaData, Table, Column, Integer, String, ForeignKey,
    create_engine, select, insert, update, delete, bindparam,
)
from sqlalchemy.orm import registry, relationship
from sqlalchemy.dialects import mysql


engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
metadata_obj = MetaData()

user_table = Table(
    "user_account", metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(30)),
    Column("fullname", String),
)

address_table = Table(
    "address", metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("user_account.id"), nullable=False),
    Column("email_address", String, nullable=False)
)

metadata_obj.create_all(engine)

mapped_registry = registry()
Base = mapped_registry.generate_base()


class User(Base):
    __tablename__ = "user_account"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String)
    
    addresses = relationship("Address", back_populates="user")
    
    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Address(Base):
    __tablename__ = "address"
    
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user_account.id"))
    
    user = relationship("User", back_populates="addresses")
    
    def __repr__(self):
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


mapped_registry.metadata.create_all(engine)


stmt = insert(user_table).values(name="spongebob", fullname="Spongebob Squarepants")
with engine.connect() as conn:
    result = conn.execute(stmt)
    conn.commit()

with engine.connect() as conn:
    result = conn.execute(
        insert(user_table),
        [
            {"name": "sandy", "fullname": "Sandy Cheeks"},
            {"name": "patrick", "fullname": "Patrick Star"}
        ]
    )
    conn.commit()

scalar_subq = (
    select(user_table.c.id).
    where(user_table.c.name == bindparam("username")).
    scalar_subquery()
)

with engine.connect() as conn:
    result = conn.execute(
        insert(address_table).values(user_id=scalar_subq),
        [
            {"username": 'spongebob', "email_address": "spongebob@sqlalchemy.org"},
            {"username": 'sandy', "email_address": "sandy@sqlalchemy.org"},
            {"username": 'sandy', "email_address": "sandy@squirrelpower.org"},
        ]
    )
    conn.commit()

stmt = (
    update(user_table).where(user_table.c.name == "patrick").
    values(fullname="Patrick the Star")
)
print(stmt)

stmt = update(user_table).values(fullname="Username: " + user_table.c.name)
print(stmt)

stmt = (
    update(user_table).
    where(user_table.c.name == bindparam("oldname")).
    values(name=bindparam("newname"))
)

with engine.connect() as conn:
    conn.execute(
        stmt,
        [
            {'oldname':'jack', 'newname':'ed'},
            {'oldname':'wendy', 'newname':'mary'},
            {'oldname':'jim', 'newname':'jake'},
        ]
    )

scalar_subq = (
    select(address_table.c.email_address).
    where(address_table.c.user_id == user_table.c.id).
    order_by(address_table.c.id).
    limit(1).scalar_subquery()
)

update_stmt = update(user_table).values(fullname=scalar_subq)
print(update_stmt)

update_stmt = (
    update(user_table).
    where(user_table.c.id == address_table.c.user_id).
    where(address_table.c.email_address == "patrick@aol.com").
    values(
        {
            user_table.c.fullname: "Pat",
            address_table.c.email_address: "pat@aol.com",
        }
    )
)
print(update_stmt.compile(dialect=mysql.dialect()))

update_stmt = (
    update(user_table).
    ordered_values(
        (user_table.c.name, "patrick"),
        (user_table.c.fullname, user_table.c.name + "surname")
    )
)
print(update_stmt)

stmt = delete(user_table).where(user_table.c.name == "patrick")
print(stmt)

delete_stmt = (
    delete(user_table).
    where(user_table.c.id == address_table.c.user_id).
    where(address_table.c.email_address == "patrick@aol.com")
)
print(delete_stmt)

with engine.begin() as conn:
    result = conn.execute(
        update(user_table).
        values(fullname="Patrick McStar").
        where(user_table.c.name == "patrick")
    )
    print(result.rowcount)

update_stmt = (
    update(user_table).where(user_table.c.name == "patrick").
    values(fullname="Patrick the Star").
    returning(user_table.c.id, user_table.c.name)
)
print(update_stmt)

delete_stmt = (
    delete(user_table).where(user_table.c.name == "patrick").
    returning(user_table.c.id, user_table.c.name)
)
print(delete_stmt)
