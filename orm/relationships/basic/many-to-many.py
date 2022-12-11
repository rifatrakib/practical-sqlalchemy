from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

association_table = Table(
    "association_table",
    Base.metadata,
    Column("left_id", ForeignKey("left_table.id")),
    Column("right_id", ForeignKey("right_table.id")),
)

middle_table = Table(
    "middle_table",
    Base.metadata,
    Column("left_id", ForeignKey("left.id"), primary_key=True),
    Column("right_id", ForeignKey("right.id"), primary_key=True),
)

mid = Table(
    "mid",
    Base.metadata,
    Column("left_id", ForeignKey("lt.id"), primary_key=True),
    Column("right_id", ForeignKey("rt.id"), primary_key=True),
)


class Parent(Base):
    __tablename__ = "left_table"
    id = Column(Integer, primary_key=True)
    children = relationship("Child", secondary=association_table)


class Child(Base):
    __tablename__ = "right_table"
    id = Column(Integer, primary_key=True)


class Left(Base):
    __tablename__ = "left"
    id = Column(Integer, primary_key=True)
    children = relationship("Right", secondary=middle_table, back_populates="parents")


class Right(Base):
    __tablename__ = "right"
    id = Column(Integer, primary_key=True)
    parents = relationship("Left", secondary=middle_table, back_populates="children")


class LT(Base):
    __tablename__ = "lt"
    id = Column(Integer, primary_key=True)
    children = relationship("RT", secondary=mid, backref="parents")


class RT(Base):
    __tablename__ = "rt"
    id = Column(Integer, primary_key=True)
