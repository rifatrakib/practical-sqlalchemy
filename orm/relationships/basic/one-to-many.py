from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Parent(Base):
    __tablename__ = "parent_table"
    id = Column(Integer, primary_key=True)
    children = relationship("Child")


class Child(Base):
    __tablename__ = "child_table"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("parent_table.id"))


class ParentModel(Base):
    __tablename__ = "parents"
    id = Column(Integer, primary_key=True)
    children = relationship("ChildModel", back_populates="parent")


class ChildModel(Base):
    __tablename__ = "children"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("parents.id"))
    parent = relationship("ParentModel", back_populates="children")


class ParentTable(Base):
    __tablename__ = "table_parents"
    id = Column(Integer, primary_key=True)
    children = relationship("ChildModel", backref="parent")
