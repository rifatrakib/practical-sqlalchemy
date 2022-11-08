from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import (
    declared_attr, declarative_mixin, declarative_base, has_inherited_table
)

Base = declarative_base()


@declarative_mixin
class TablenameMixin:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class Person(TablenameMixin, Base):
    id = Column(Integer, primary_key=True)
    discriminator = Column("type", String(50))
    
    __mapper_args__ = {"polymorphic_on": discriminator}


class Engineer(Person):
    __tablename__ = None
    __mapper_args__ = {"polymorphic_identity": "engineer"}
    primary_language = Column(String(50))


@declarative_mixin
class InheritedTablenameMixin:
    @declared_attr
    def __tablename__(cls):
        if has_inherited_table(cls):
            return None
        return cls.__name__.lower()


class PersonParent(InheritedTablenameMixin, Base):
    id = Column(Integer, primary_key=True)
    discriminator = Column("type", String(50))
    
    __mapper_args__ = {"polymorphic_on": discriminator}


class EngineerInheritor(PersonParent):
    primary_language = Column(String(50))
    __mapper_args__ = {"polymorphic_identity": "engineerinheritor"}
