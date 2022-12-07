from sqlalchemy import Column, Integer, String, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"mysql_engine": "InnoDB"}
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)


class TupleUser(Base):
    __tablename__ = "tuple_user"
    __table_args__ = (
        ForeignKeyConstraint(["id"], ["user.id"]),
        UniqueConstraint("name"),
    )
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)


class MixedUser(Base):
    __tablename__ = "mixed_user"
    __table_args__ = (
        ForeignKeyConstraint(["id"], ["user.id"]),
        UniqueConstraint("name"),
        {"mysql_engine": "InnoDB"},
    )
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)
