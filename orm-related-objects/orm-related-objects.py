from sqlalchemy import (
    Column, Integer, String, ForeignKey, create_engine,
    select, insert, bindparam,
)
from sqlalchemy.orm import (
    Session, registry, aliased, with_parent, relationship,
    selectinload, joinedload, contains_eager,
)

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
mapped_registry = registry()
Base = mapped_registry.generate_base()
session = Session(engine)


class User(Base):
    __tablename__ = "user_account"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String)
    
    addresses = relationship("Address", back_populates="user", lazy="selectin")
    
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


class UserStrict(Base):
    __tablename__ = "user_strict"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String)
    
    addresses = relationship("AddressStrict", back_populates="user", lazy="raise_on_sql")
    
    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class AddressStrict(Base):
    __tablename__ = "address_strict"
    
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user_account.id"))
    
    user = relationship("User", back_populates="addresses", lazy="raise_on_sql")
    
    def __repr__(self):
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


mapped_registry.metadata.create_all(engine)

spongebob = User(name="spongebob", fullname="Spongebob Squarepants")
sandy = User(name="sandy", fullname="Sandy Cheeks")
patrick = User(name="patrick", fullname="Patrick Star")
squidward = User(name="squidward", fullname="Squidward Tentacles")
krabs = User(name="ehkrabs", fullname="Eugene H. Krabs")

session.add(spongebob)
session.add(sandy)
session.add(patrick)
session.add(squidward)
session.add(krabs)

session.flush()
session.commit()

addresses = [
    {"username": "spongebob", "email_address": "spongebob@sqlalchemy.org"},
    {"username": "sandy", "email_address": "sandy@sqlalchemy.org"},
    {"username": "sandy", "email_address": "sandy@squirrelpower.org"},
]
scalar_subq = (
    select(User.id).
    where(User.name == bindparam("username")).
    scalar_subquery()
)

with engine.connect() as conn:
    result = conn.execute(
        insert(Address).values(user_id=scalar_subq),
        [
            {"username": 'spongebob', "email_address": "spongebob@sqlalchemy.org"},
            {"username": 'sandy', "email_address": "sandy@sqlalchemy.org"},
            {"username": 'sandy', "email_address": "sandy@squirrelpower.org"},
        ]
    )
    conn.commit()

u1 = User(name="pkrabs", fullname="Pearl Krabs")
print(f"{u1.addresses = }")

a1 = Address(email_address="pearl.krabs@gmail.com")
u1.addresses.append(a1)
print(f"{u1.addresses = }")
print(f"{a1.user = }")

a2 = Address(email_address="pearl@aol.com", user=u1)
print(f"{u1.addresses = }")

# equivalent effect as a2 = Address(user=u1)
a2.user = u1

session.add(u1)
print(f"{u1 in session = }")
print(f"{a1 in session = }")
print(f"{a2 in session = }")

print(f"{u1.id = }")
print(f"{a1.user_id = }")

session.commit()

print(f"{u1.id = }")
print(f"{u1.addresses = }")

print(f"{u1.addresses = }")

print(f"{a1 = }")
print(f"{a2 = }")

print(select(Address.email_address).select_from(User).join(User.addresses))
print(select(Address.email_address).join_from(User, Address))

address_alias_1 = aliased(Address)
address_alias_2 = aliased(Address)

print(
    select(User).
    join(User.addresses.of_type(address_alias_1)).
    where(address_alias_1.email_address == "patrick@aol.com").
    join(User.addresses.of_type(address_alias_2)).
    where(address_alias_2.email_address == "patrick@gmail.com")
)

user_alias_1 = aliased(User)
print(select(user_alias_1.name).join(user_alias_1.addresses))

stmt = select(User.fullname).join(
    User.addresses.and_(Address.email_address == "pearl.krabs@gmail.com")
)
session.execute(stmt).all()

stmt = select(User.fullname).where(
    User.addresses.any(Address.email_address == "pearl.krabs@gmail.com")
)
session.execute(stmt).all()

stmt = select(User.fullname).where(~User.addresses.any())
session.execute(stmt).all()

stmt = select(Address.email_address).where(Address.user.has(User.name == "pkrabs"))
session.execute(stmt).all()

print(select(Address).where(Address.user == u1))
print(select(Address).where(Address.user != u1))
print(select(User).where(User.addresses.contains(a1)))
print(select(Address).where(with_parent(u1, User.addresses)))

for user_obj in session.execute(
    select(User).options(selectinload(User.addresses))
).scalars():
    print(f"{user_obj.addresses = }")

stmt = select(User).options(selectinload(User.addresses)).order_by(User.id)
for row in session.execute(stmt):
    print(f"{row.User.name} ({', '.join(a.email_address for a in row.User.addresses)})")

stmt = (
    select(Address).options(joinedload(Address.user, innerjoin=True)).
    order_by(Address.id)
)
for row in session.execute(stmt):
    print(f"{row.Address.email_address} {row.Address.user.name}")

stmt = (
    select(Address).
    join(Address.user).
    where(User.name == "pkrabs").
    options(contains_eager(Address.user)).
    order_by(Address.id)
)
for row in session.execute(stmt):
    print(f"{row.Address.email_address} {row.Address.user.name}")

stmt = (
    select(Address).
    join(Address.user).
    where(User.name == "pkrabs").
    options(joinedload(Address.user)).
    order_by(Address.id)
)
print(stmt)

stmt = (
    select(User).
    options(
        selectinload(User.addresses.and_(~Address.email_address.endswith("sqlalchemy.org")))
    ).order_by(User.id).execution_options(populate_existing=True)
)

for row in session.execute(stmt):
    print(f"{row.User.name} ({', '.join(a.email_address for a in row.User.addresses)})")

spongebob_strict = UserStrict(name="spongebob", fullname="Spongebob Squarepants")
sandy_strict = UserStrict(name="sandy", fullname="Sandy Cheeks")
patrick_strict = UserStrict(name="patrick", fullname="Patrick Star")
squidward_strict = UserStrict(name="squidward", fullname="Squidward Tentacles")
krabs_strict = UserStrict(name="ehkrabs", fullname="Eugene H. Krabs")

session.add(spongebob_strict)
session.add(sandy_strict)
session.add(patrick_strict)
session.add(squidward_strict)
session.add(krabs_strict)

session.flush()
session.commit()

addresses = [
    {"username": "spongebob", "email_address": "spongebob@sqlalchemy.org"},
    {"username": "sandy", "email_address": "sandy@sqlalchemy.org"},
    {"username": "sandy", "email_address": "sandy@squirrelpower.org"},
]
scalar_subq = (
    select(UserStrict.id).
    where(UserStrict.name == bindparam("username")).
    scalar_subquery()
)

with engine.connect() as conn:
    result = conn.execute(
        insert(AddressStrict).values(user_id=scalar_subq),
        [
            {"username": 'spongebob', "email_address": "spongebob@sqlalchemy.org"},
            {"username": 'sandy', "email_address": "sandy@sqlalchemy.org"},
            {"username": 'sandy', "email_address": "sandy@squirrelpower.org"},
        ]
    )
    conn.commit()

try:
    u1 = session.execute(select(UserStrict)).scalars().first()
    print(f"{u1.addresses = }")
except Exception as e:
    print(f"{type(e)}")
    print(f"{str(e)}")

u1 = session.execute(select(UserStrict).options(selectinload(UserStrict.addresses))).scalars().first()
print(f"{u1 = }")
