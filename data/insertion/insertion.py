from sqlalchemy import (
    MetaData, Table, Column, Integer, String,
    ForeignKey, create_engine, insert, select, bindparam,
)


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

stmt = insert(user_table).values(name="spongebob", fullname="Spongebob Squarepants")
print(stmt)

compiled = stmt.compile()
compiled.params

with engine.connect() as conn:
    result = conn.execute(stmt)
    conn.commit()

result.inserted_primary_key

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

select_stmt = select(user_table.c.id, user_table.c.name + "@aol.com")
insert_stmt = insert(address_table).from_select(
    ["user_id", "email_address"], select_stmt,
)
print(insert_stmt)

insert_stmt = insert(address_table).returning(address_table.c.id, address_table.c.email_address)
print(insert_stmt)

select_stmt = select(user_table.c.id, user_table.c.name + "@aol.com")
insert_stmt = insert(address_table).from_select(
    ["user_id", "email_address"], select_stmt,
)
print(insert_stmt.returning(address_table.c.id, address_table.c.email_address))
