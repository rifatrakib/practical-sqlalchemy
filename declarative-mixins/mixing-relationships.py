from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import declared_attr, declarative_base, declarative_mixin, relationship

Base = declarative_base()


@declarative_mixin
class RefTargetMixin:
    @declared_attr
    def target_id(cls):
        return Column("target_id", ForeignKey("target.id"))
    
    @declared_attr
    def target(cls):
        return relationship("Target")


class Foo(RefTargetMixin, Base):
    __tablename__ = "foo"
    
    id = Column(Integer, primary_key=True)


class Bar(RefTargetMixin, Base):
    __tablename__ = "bar"
    
    id = Column(Integer, primary_key=True)


class Target(Base):
    __tablename__ = "target"
    
    id = Column(Integer, primary_key=True)

"""
@declarative_mixin
class WrongParamRefTargetMixin:
    @declared_attr
    def target_id(cls):
        return Column("target_id", ForeignKey("target.id"))
    
    @declared_attr
    def target(cls):
        return relationship(Target, primaryjoin=Target.id == cls.target_id) # this is *incorrect*
"""


@declarative_mixin
class ParamRefTargetMixin:
    @declared_attr
    def target_id(cls):
        return Column("target_id", ForeignKey("target.id"))
    
    @declared_attr
    def target(cls):
        return relationship(Target, primaryjoin=lambda: Target.id == cls.target_id)


@declarative_mixin
class AlternativeParamRefTargetMixin:
    @declared_attr
    def target_id(cls):
        return Column("target_id", ForeignKey("target.id"))
    
    @declared_attr
    def target(cls):
        return relationship(Target, primaryjoin=f"Target.id == {cls.__name__}.target_id")
