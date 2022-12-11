from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Association(Base):
    __tablename__ = "association_table"
    left_id = Column(ForeignKey("left_table.id"), primary_key=True)
    right_id = Column(ForeignKey("right_table.id"), primary_key=True)
    extra_data = Column(String(50))
    child = relationship("Child")


class Parent(Base):
    __tablename__ = "left_table"
    id = Column(Integer, primary_key=True)
    children = relationship("Association")


class Child(Base):
    __tablename__ = "right_table"
    id = Column(Integer, primary_key=True)


class AssociationModel(Base):
    __tablename__ = "association"
    left_id = Column(ForeignKey("left.id"), primary_key=True)
    right_id = Column(ForeignKey("right.id"), primary_key=True)
    extra_data = Column(String(50))
    child = relationship("ChildModel", back_populates="parents")
    parent = relationship("ParentModel", back_populates="children")


class ParentModel(Base):
    __tablename__ = "left"
    id = Column(Integer, primary_key=True)
    children = relationship("AssociationModel", back_populates="parent")


class ChildModel(Base):
    __tablename__ = "right"
    id = Column(Integer, primary_key=True)
    parents = relationship("AssociationModel", back_populates="child")
