from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Parent(Base):
    __tablename__ = "parent_table"
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("child_table.id"))
    child = relationship("Child")


class Child(Base):
    __tablename__ = "child_table"
    id = Column(Integer, primary_key=True)


class ParentModel(Base):
    __tablename__ = "parent"
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("child.id"))
    child = relationship("ChildModel", back_populates="parents")


class ChildModel(Base):
    __tablename__ = "child"
    id = Column(Integer, primary_key=True)
    parents = relationship("ParentModel", back_populates="child")


class ParentTable(Base):
    __tablename__ = "table_parent"
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("child.id"))
    child = relationship("ChildModel", backref="parents")
