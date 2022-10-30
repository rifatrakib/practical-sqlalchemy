from sqlalchemy import Column, Integer, String, Table, inspect, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)


# equivalent Table object produced
user_table = Table(
    "equivalent_user",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("fullname", String),
    Column("nickname", String),
)

user_table = User.__table__
print(f"{user_table = }")

user_table = inspect(User).local_table
print(f"{user_table = }")
