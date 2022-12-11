from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import backref, declarative_base, relationship

Base = declarative_base()


class Parent(Base):
    __tablename__ = "parent_table"
    id = Column(Integer, primary_key=True)
    # one-to-many collection
    children = relationship("Child", back_populates="parent")


class Child(Base):
    __tablename__ = "child_table"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("parent_table.id"))
    # many-to-one scalar
    parent = relationship("Parent", back_populates="children")


class ParentModel(Base):
    __tablename__ = "parent"
    id = Column(Integer, primary_key=True)
    # previously one-to-many Parent.children is now one-to-one Parent.child
    child = relationship("ChildModel", back_populates="parent", uselist=False)


class ChildModel(Base):
    __tablename__ = "child"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("parent.id"))
    # many-to-one side remains, see tip below
    parent = relationship("ParentModel", back_populates="child")


class ParentTable(Base):
    __tablename__ = "table_parent"
    id = Column(Integer, primary_key=True)


class ChildTable(Base):
    __tablename__ = "table_child"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("table_parent.id"))
    parent = relationship("ParentTable", backref=backref("child", uselist=False))
