from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import backref, declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    posts = relationship("Post", lazy="dynamic")


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    headline = Column(String(100))
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref=backref("posts", lazy="dynamic"))


class ParentClass(Base):
    __tablename__ = "some_table"
    id = Column(Integer, primary_key=True)
    children = relationship("ChildClass", lazy="noload")


class ChildClass(Base):
    __tablename__ = "other_table"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("some_table.id"))


class RaiseLoadClass(Base):
    __tablename__ = "raiseload_table"
    id = Column(Integer, primary_key=True)
    children = relationship("LazyClass", lazy="raise")


class LazyClass(Base):
    __tablename__ = "lazy_table"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("raiseload_table.id"))
