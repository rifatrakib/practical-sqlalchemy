from sqlalchemy import (
    Column, Integer, String, ForeignKey,
    create_engine, select, update, delete
)
from sqlalchemy.orm import Session, registry, relationship


engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
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


sandy = User(name="sandy", fullname="Sandy Cheeks")
patrick = User(name="patrick", fullname="Patrick Star")
squidward = User(name="squidward", fullname="Squidward Tentacles")
krabs = User(name="ehkrabs", fullname="Eugene H. Krabs")
print(f"{squidward = }")

session = Session(engine)
session.add(sandy)
session.add(patrick)
session.add(squidward)
session.add(krabs)
print(f"{session.new = }")
session.flush()
print(f"{squidward.id = }")
print(f"{krabs.id = }")

some_squidward = session.get(User, 3)
print(f"{some_squidward = }")
print(f"{some_squidward is squidward = }")

sandy = session.execute(select(User).filter_by(name="sandy")).scalar_one()
print(f"{sandy = }")
sandy.fullname = "Sandy Squirrel"
print(f"{sandy in session.dirty = }")
sandy_fullname = session.execute(select(User.fullname).where(User.id == 1)).scalar_one()
print(f"{sandy_fullname = }")
print(f"{sandy in session.dirty = }")

session.execute(
    update(User).
    where(User.name == "sandy").
    values(fullname="Sandy Squirrel Extraordinaire")
)
print(f"{sandy.fullname = }")

patrick = session.get(User, 2)
session.delete(patrick)
session.execute(select(User).where(User.name == "patrick")).first()
print(f"{patrick in session = }")

# refresh the target object for demonstration purposes
# only, not needed for the DELETE
squidward = session.get(User, 3)
session.execute(delete(User).where(User.name == "squidward"))
print(f"{squidward in session = }")

session.rollback()
print(f"{sandy.__dict__ = }")

print(f"{sandy.fullname = }")
print(f"{sandy.__dict__ = }")
print(f"{patrick in session = }")
print(f"{session.execute(select(User).where(User.name == 'patrick')).scalar_one() is patrick = }")

session.close()

try:
    print(f"{squidward.name = }")
except Exception as e:
    print(str(e))

session.add(squidward)
print(f"{squidward.name = }")
