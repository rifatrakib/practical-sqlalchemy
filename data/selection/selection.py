from sqlalchemy import (
    MetaData, Table, Column, Integer, String, ForeignKey, JSON,
    create_engine, literal_column, insert, select, bindparam,
    func, cast, text, and_, or_, desc, union_all, type_coerce,
)
from sqlalchemy.orm import Session, registry, aliased, relationship
from sqlalchemy.dialects import postgresql, mysql, oracle
import json


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

stmt = select(user_table).where(user_table.c.name == "spongebob")
print(stmt)

with engine.connect() as conn:
    for row in conn.execute(stmt):
        print(row)

stmt = select(User).where(User.name == "spongebob")
with Session(engine) as session:
    for row in session.execute(stmt):
        print(row)

print(select(user_table))
print(select(user_table.c.name, user_table.c.fullname))

print(select(User))

row = session.execute(select(User)).first()
print(row)
print(row[0])

user = session.scalars(select(User)).first()
print(user)

print(select(User.name, User.fullname))

row = session.execute(select(User.name, User.fullname)).first()
print(row)

session.execute(
    select(User.name, Address).
    where(User.id==Address.id).
    order_by(Address.id)
).all()

stmt = (
    select(
        ("Username: " + user_table.c.name).label("username"),
    ).order_by(user_table.c.name)
)

with engine.connect() as conn:
    for row in conn.execute(stmt):
        print(f"{row.username}")

stmt = (
    select(
        text("'some phrase'"), user_table.c.name
    ).order_by(user_table.c.name)
)

with engine.connect() as conn:
    print(conn.execute(stmt).all())

stmt = (
    select(
        literal_column("'some phrase'").label("p"), user_table.c.name,
    ).order_by(user_table.c.name)
)

with engine.connect() as conn:
    for row in conn.execute(stmt):
        print(f"{row.p}, {row.name}")

print(user_table.c.name == "squidward")
print(address_table.c.user_id > 10)
print(select(user_table).where(user_table.c.name == "squidward"))

print(
    select(address_table.c.email_address).
    where(user_table.c.name == "squidward").
    where(address_table.c.user_id == user_table.c.id)
)

print(
    select(address_table.c.email_address).
    where(
        user_table.c.name == "squidward",
        address_table.c.user_id == user_table.c.id
    )
)

print(
    select(Address.email_address).
    where(
        and_(
            or_(User.name == "squidward", User.name == "sandy"),
            Address.user_id == User.id
        )
    )
)

print(select(User).filter_by(name="spongebob", fullname="Spongebob Squarepants"))

print(select(user_table.c.name))
print(select(user_table.c.name, address_table.c.email_address))

print(
    select(user_table.c.name, address_table.c.email_address).
    join_from(user_table, address_table)
)

print(
    select(user_table.c.name, address_table.c.email_address).
    join(address_table)
)

print(
    select(address_table.c.email_address).
    select_from(user_table).join(address_table)
)

print(select(func.count("*")).select_from(user_table))

print(
    select(address_table.c.email_address).
    select_from(user_table).
    join(address_table, user_table.c.id == address_table.c.user_id)
)

print(select(user_table).join(address_table, isouter=True))
print(select(user_table).join(address_table, full=True))

print(select(user_table).order_by(user_table.c.name))
print(select(User).order_by(User.fullname.desc()))

count_fn = func.count(user_table.c.id)
print(count_fn)

with engine.connect() as conn:
    result = conn.execute(
        select(User.name, func.count(Address.id).label("count")).
        join(Address).group_by(User.name).having(func.count(Address.id) > 1)
    )
    print(result.all())

stmt = select(
    Address.user_id, func.count(Address.id).label("num_addresses")
).group_by("user_id").order_by("user_id", desc("num_addresses"))
print(stmt)

user_alias_1 = user_table.alias()
user_alias_2 = user_table.alias()

print(
    select(user_alias_1.c.name, user_alias_2.c.name).
    join_from(user_alias_1, user_alias_2, user_alias_1.c.id > user_alias_2.c.id)
)

address_alias_1 = aliased(Address)
address_alias_2 = aliased(Address)

print(
    select(User).
    join_from(User, address_alias_1).
    where(address_alias_1.email_address == "patrick@aol.com").
    join_from(User, address_alias_2).
    where(address_alias_2.email_address == "patrick@gmail.com")
)

subq = select(
    func.count(address_table.c.id).label("count"),
    address_table.c.user_id,
).group_by(address_table.c.user_id).subquery()
print(subq)
print(select(subq.c.user_id, subq.c.count))

stmt = select(
    user_table.c.name,
    user_table.c.fullname,
    subq.c.count,
).join_from(user_table, subq)
print(stmt)

subq = select(
    func.count(address_table.c.id).label("count"),
    address_table.c.user_id
).group_by(address_table.c.user_id).cte()
stmt = select(
    user_table.c.name,
    user_table.c.fullname,
    subq.c.count,
).join_from(user_table, subq)
print(stmt)

subq = select(Address).where(~Address.email_address.like("%@aol.com")).subquery()
address_subq = aliased(Address, subq)
stmt = select(User, address_subq).join_from(User, address_subq).order_by(User.id, address_subq.id)

with Session(engine) as session:
    for user, address in session.execute(stmt):
        print(f"{user=} {address=}")

cte_obj = select(Address).where(~Address.email_address.like("%@aol.com")).cte()
address_cte = aliased(Address, cte_obj)
stmt = select(User, address_cte).join_from(User, address_cte).order_by(User.id, address_cte.id)

with Session(engine) as session:
    for user, address in session.execute(stmt):
        print(f"{user=} {address=}")

subq = select(
    func.count(address_table.c.id)
).where(user_table.c.id == address_table.c.user_id).scalar_subquery()
print(subq)
print(subq == 5)

stmt = select(user_table.c.name, subq.label("address_count"))
print(stmt)

try:
    stmt = select(
        user_table.c.name,
        address_table.c.email_address,
        subq.label("address_count"),
    ).join_from(user_table, address_table).order_by(user_table.c.id, address_table.c.id)
    print(stmt)
except Exception as e:
    print(str(e))

subq = select(
    func.count(address_table.c.id)
).where(user_table.c.id == address_table.c.user_id).\
scalar_subquery().correlate(user_table)

with engine.connect() as conn:
    result = conn.execute(
        select(
            user_table.c.name,
            address_table.c.email_address,
            subq.label("address_count")
        ).
        join_from(user_table, address_table).
        order_by(user_table.c.id, address_table.c.id)
    )
print(result.all())

subq = (
    select(
        func.count(address_table.c.id).label("address_count"),
        address_table.c.email_address,
        address_table.c.user_id,
    ).
    where(user_table.c.id == address_table.c.user_id).
    lateral()
)

stmt = (
    select(
        user_table.c.name,
        subq.c.address_count,
        subq.c.email_address,
    ).
    join_from(user_table, subq).
    order_by(user_table.c.id, subq.c.email_address)
)
print(stmt)

stmt1 = select(user_table).where(user_table.c.name == "sandy")
stmt2 = select(user_table).where(user_table.c.name == "spongebob")
u = union_all(stmt1, stmt2)

with engine.connect() as conn:
    result = conn.execute(u)
    print(result.all())

u_subq = u.subquery()
stmt = (
    select(u_subq.c.name, address_table.c.email_address).
    join_from(address_table, u_subq).
    order_by(u_subq.c.name, address_table.c.email_address)
)

with engine.connect() as conn:
    result = conn.execute(stmt)
    print(result.all())

stmt1 = select(User).where(User.name == "sandy")
stmt2 = select(User).where(User.name == "spongebob")
u = union_all(stmt1, stmt2)
print(u)

orm_stmt = select(User).from_statement(u)
with Session(engine) as session:
    for obj in session.execute(orm_stmt).scalars():
        print(obj)

user_alias = aliased(User, u.subquery())
orm_stmt = select(user_alias).order_by(user_alias.id)
with Session(engine) as session:
    for obj in session.execute(orm_stmt).scalars():
        print(obj)

subq = (
    select(func.count(address_table.c.id)).
    where(user_table.c.id == address_table.c.user_id).
    group_by(address_table.c.user_id).
    having(func.count(address_table.c.id) > 1)
).exists()

with engine.connect() as conn:
    result = conn.execute(select(user_table.c.name).where(subq))
    print(result.all())

subq = (
    select(address_table.c.id).
    where(user_table.c.id == address_table.c.user_id)
).exists()

with engine.connect() as conn:
    result = conn.execute(select(user_table.c.name).where(~subq))
    print(result.all())

print(select(func.count()).select_from(user_table))
print(select(func.lower("A String With Much UPPERCASE")))

stmt = select(func.now())
with engine.connect() as conn:
    result = conn.execute(stmt)
    print(result.all())

print(select(func.some_crazy_function(user_table.c.name, 17)))

print(select(func.now()).compile(dialect=postgresql.dialect()))
print(select(func.now()).compile(dialect=oracle.dialect()))

function_expr = func.json_object("{a, 1, b, 'def', c, 3.5", type_=JSON)
stmt = select(function_expr["def"])
print(stmt)

m1 = func.max(Column("some_int", Integer))
print(m1.type)
m2 = func.max(Column("some_str", String))
print(m2.type)
print(func.now().type)
print(func.current_date().type)
print(func.concat("x", "y").type)
print(func.upper("lowercase").type)
print(select(func.upper("lowercase") + " suffix"))
print(func.count().type)
print(func.json_object("{'a', 'b'}").type)

stmt = select(
    func.row_number().over(partition_by=user_table.c.name),
    user_table.c.name,
    address_table.c.email_address,
).select_from(user_table).join(address_table)

with engine.connect() as conn:
    result = conn.execute(stmt)
    print(result.all())

stmt = select(
    func.count().over(order_by=user_table.c.name),
    user_table.c.name,
    address_table.c.email_address,
).select_from(user_table).join(address_table)

with engine.connect() as conn:
    result = conn.execute(stmt)
    print(result.all())

print(func.unnest(func.percentile_disc([0.25,0.5,0.75,1]).within_group(user_table.c.name)))

stmt = select(
    func.count(address_table.c.email_address).filter(user_table.c.name == "sandy"),
    func.count(address_table.c.email_address).filter(user_table.c.name == "spongebob"),
).select_from(user_table).join(address_table)

with engine.connect() as conn:
    result = conn.execute(stmt)
    print(result.all())

onetwothree = func.json_each('["one", "two", "three"]').table_valued("value")
stmt = select(onetwothree).where(onetwothree.c.value.in_(["two", "three"]))

with engine.connect() as conn:
    result = conn.execute(stmt)
    print(result.all())

stmt = select(func.json_array_elements('["one", "two"]').column_valued("x"))
print(stmt)

stmt = select(func.scalar_strings(5).column_valued("s"))
print(stmt.compile(dialect=oracle.dialect()))

stmt = select(cast(user_table.c.id, String))
with engine.connect() as conn:
    result = conn.execute(stmt)
    print(result.all())

print(cast("{'a': 'b'}", JSON)["a"])

stmt = select(type_coerce({'some_key': {'foo': 'bar'}}, JSON)["some_key"])
print(stmt.compile(dialect=mysql.dialect()))
