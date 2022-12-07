import sqlalchemy
from sqlalchemy.sql import exists
from sqlalchemy import (
    Table, Column, Integer, String, Text,
    ForeignKey, create_engine, text, func,
)
from sqlalchemy.orm import (
    sessionmaker, declarative_base, aliased,
    relationship, selectinload, joinedload, contains_eager,
)

print(f"{sqlalchemy.__version__ = }")

engine = create_engine("sqlite:///:memory:", echo=True)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)
    
    addresses = relationship("Address", back_populates="user", cascade="all, delete, delete-orphan")
    
    def __repr__(self):
        return f"<User(name={self.name}, fullname={self.fullname}, nickname={self.nickname})>"


class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="addresses")
    
    def __repr__(self):
        return f"<Address(email_address={self.email_address})>"


print(f"{User.__table__ = }")

Base.metadata.create_all(engine)

ed_user = User(name="ed", fullname="Ed Jones", nickname="edsnickname")
print(f"{ed_user.name = }, {ed_user.nickname = }, {ed_user.id = }")

Session = sessionmaker(bind=engine)

Session = sessionmaker()
Session.configure(bind=engine)

session = Session()

ed_user = User(name="ed", fullname="Ed Jones", nickname="edsnickname")
session.add(ed_user)

our_user = session.query(User).filter_by(name="ed").first()
print(f"{our_user = }")
print(f"{ed_user is our_user = }")

ed_user.nickname = "eddie"
print(f"{session.dirty = }")
print(f"{session.new = }")

session.commit()

print(f"{ed_user.id = }")

ed_user.name = "Edwardo"
fake_user = User(name="fakeuser", fullname="Invalid", nickname="12345")
session.add(fake_user)

session.query(User).filter(User.name.in_(["Edwardo", "fakeuser"])).all()

session.rollback()
print(f"{ed_user.name = }")
print(f"{fake_user in session = }")

session.query(User).filter(User.name.in_(["ed", "fakeuser"])).all()

for instance in session.query(User).order_by(User.id):
    print(instance.name, instance.fullname)

for name, fullname in session.query(User.name, User.fullname):
    print(name, fullname)

for row in session.query(User, User.name).all():
    print(row.User, row.name)

for row in session.query(User.name.label("name_label")).all():
    print(row.name_label)

user_alias = aliased(User, name="user_alias")
for row in session.query(user_alias, user_alias.name).all():
    print(row.user_alias)

for u in session.query(User).order_by(User.id)[1:3]:
    print(u)

for (name,) in session.query(User.name).filter_by(fullname="Ed Jones"):
    print(name)

for (name,) in session.query(User.name).filter(User.fullname == "Ed Jones"):
    print(name)

for user in (
    session.query(User).
    filter(User.name == "ed").
    filter(User.fullname == "Ed Jones")
):
    print(user)

query = session.query(User).filter(User.name.like("%ed%")).order_by(User.id)
print(f"{query.all() = }")
print(f"{query.first() = }")

try:
    user = query.one()
except Exception as e:
    print(str(e))

try:
    user = query.filter(User.id == 99).one()
except Exception as e:
    print(str(e))

query = session.query(User.id).filter(User.name == "ed").order_by(User.id)
print(f"{query.scalar() = }")

for user in session.query(User).filter(text("id < 224")).order_by(text("id")).all():
    print(user.name)

result = session.query(User).filter(text("id < :value and name = :name")).params(
    value=224, name="fred"
).order_by(User.id).one()
print(f"{result = }")

result = session.query(User).from_statement(text(
    "SELECT * FROM users where name=:name"
)).params(name="ed").all()
print(f"{result = }")

stmt = text("SELECT name, id, fullname, nickname " "FROM users WHERE name = :name")
stmt = stmt.columns(User.name, User.id, User.fullname, User.nickname)
result = session.query(User).from_statement(stmt).params(name="ed").all()
print(f"{result = }")

stmt = text("SELECT name, id FROM users WHERE name = :name")
stmt = stmt.columns(User.name, User.id)
result = session.query(User.id, User.name).from_statement(stmt).params(name="ed").all()
print(f"{result = }")

counts = session.query(User).filter(User.name.like("%ed%")).count()
print(f"{counts = }")

result = session.query(func.count(User.name), User.name).group_by(User.name).all()
print(f"{result = }")

print(f"{session.query(func.count('*')).select_from(User).scalar() = }")
print(f"{session.query(func.count(User.id)).scalar() = }")

User.addresses = relationship("Address", order_by=Address.id, back_populates="user")
Base.metadata.create_all(engine)

jack = User(name="jack", fullname="Jack Bean", nickname="gjffdd")
print(f"{jack.addresses = }")
print(f"{jack.addresses[1] = }")
print(f"{jack.addresses[1].user = }")

session.add(jack)
session.commit()

jack = session.query(User).filter_by(name="jack").one()
print(f"{jack = }")
print(f"{jack.addresses = }")

for u, a in (
    session.query(User, Address).
    filter(User.id == Address.user_id).
    filter(Address.email_address == "jack@google.com").all()
):
    print(f"{u = }")
    print(f"{a = }")

result = session.query(User).join(Address).filter(
    Address.email_address == "jack@google.com"
).all()
print(f"{result = }")

print(f"{query.join(Address, User.id == Address.user_id) = }") # explicit condition
print(f"{query.join(User.addresses) = }") # specify relationship from left to right
print(f"{query.join(Address, User.addresses) = }") # same, with explicit target
# use relationship + additional ON criteria
print(f"{query.join(User.addresses.and_(Address.email_address != 'foo'))}")

adalias1 = aliased(Address)
adalias2 = aliased(Address)

for username, email1, email2 in (
    session.query(User.name, adalias1.email_address, adalias2.email_address).
    join(User.addresses.of_type(adalias1)).
    join(User.addresses.of_type(adalias2)).
    filter(adalias1.email_address == "jack@google.com").
    filter(adalias2.email_address == "j25@yahoo.com")
):
    print(f"{username = }, {email1 = }, {email2 = }")

# equivalent to query.join(User.addresses.of_type(adalias1))
q = query.join(adalias1, User.addresses)
print(f"{q = }")

stmt = (
    session.query(Address.user_id, func.count("*").label("address_count")).
    group_by(Address.user_id).subquery()
)

for u, count in (
    session.query(User, stmt.c.address_count).
    outerjoin(stmt, User.id == stmt.c.user_id).
    order_by(User.id)
):
    print(f"{u = }, {count = }")

stmt = session.query(Address).filter(Address.email_address != "j25@yahoo.com").subquery()
addr_alias = aliased(Address, stmt)
for user, address in session.query(User, addr_alias).join(addr_alias, User.addresses):
    print(f"{user = }")
    print(f"{address = }")

stmt = exists().where(Address.user_id == User.id)
for (name,) in session.query(User.name).filter(stmt):
    print(f"{name = }")

for (name,) in session.query(User.name).filter(User.addresses.any()):
    print(f"{name = }")

for (name,) in session.query(User.name).filter(
    User.addresses.any(Address.email_address.like("%google%"))
):
    print(f"{name = }")

print(f"{session.query(Address).filter(~Address.user.has(User.name == 'jack')).all() = }")

jack = (
    session.query(User).
    options(selectinload(User.addresses)).
    filter_by(name="jack").one()
)
print(f"{jack = }")
print(f"{jack.addresses = }")

jack = (
    session.query(User).
    options(joinedload(User.addresses)).
    filter_by(name="jack").one()
)
print(f"{jack = }")
print(f"{jack.addresses = }")

jacks_addresses = (
    session.query(Address).
    join(Address.user).
    filter(User.name == "jack").
    options(contains_eager(Address.user)).all()
)
print(f"{jacks_addresses = }")
print(f"{jacks_addresses[0].user = }")

jack = session.get(User, 5)
del jack.addresses[1]
session.query(Address).filter(
    Address.email_address.in_(["jack@google.com", "j25@yahoo.com"])
).count()

session.delete(jack)
session.query(User).filter_by(name="jack").count()
session.query(Address).filter(
    Address.email_address.in_(["jack@google.com", "j25@yahoo.com"])
).count()

post_keywords = Table(
    "post_keywords",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id"), primary_key=True),
    Column("keyword_id", ForeignKey("keywords.id"), primary_key=True),
)


class BlogPost(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    headline = Column(String(255), nullable=False)
    body = Column(Text)
    
    # many to many BlogPost<->Keyword
    keywords = relationship("Keyword", secondary=post_keywords, back_populates="posts")
    
    def __init__(self, headline, body, author):
        self.headline = headline
        self.body = body
        self.author = author
    
    def __repr__(self):
        return f"BlogPost({self.headline}, {self.body}, {self.author})"


class Keyword(Base):
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True)
    keyword = Column(String(50), nullable=False, unique=True)
    
    posts = relationship("BlogPost", secondary=post_keywords, back_populates="keywords")
    
    def __init__(self, keyword):
        self.keyword = keyword


BlogPost.author = relationship(User, back_populates="posts")
User.posts = relationship(BlogPost, back_populates="author", lazy="dynamic")
Base.metadata.create_all(engine)

wendy = session.query(User).filter_by(name="wendy").one()
post = BlogPost("Wendy's blog post", "This is a test", wendy)
session.add(post)

post.keywords.append(Keyword("wendy"))
post.keywords.append(Keyword("firstpost"))

session.query(BlogPost).filter(BlogPost.keywords.any(keyword="firstpost")).all()

session.query(BlogPost).filter(BlogPost.author == wendy).filter(
    BlogPost.keywords.any(keyword="firstpost")
).all()

wendy.posts.filter(BlogPost.keywords.any(keyword="firstpost")).all()
