from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import (
    declared_attr, declarative_mixin, declarative_base, has_inherited_table,
)

Base = declarative_base()


@declarative_mixin
class HasIdMixin:
    @declared_attr.cascading
    def id(cls):
        if has_inherited_table(cls):
            return Column(ForeignKey("person.id"), primary_key=True)
        else:
            return Column(Integer, primary_key=True)


class Person(HasIdMixin, Base):
    __tablename__ = "person"
    discriminator = Column("type", String(50))
    __mapper_args__ = {"polymorphic_on": discriminator}


class Engineer(Person):
    __tablename__ = "engineer"
    primary_language = Column(String(50))
    __mapper_args__ = {"polymorphic_identity": "engineer"}
