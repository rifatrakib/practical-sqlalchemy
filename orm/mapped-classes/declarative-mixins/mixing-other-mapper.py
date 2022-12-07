from sqlalchemy import Column, Integer
from sqlalchemy.orm import (
    declared_attr, declarative_base, declarative_mixin, deferred, column_property
)

Base = declarative_base()


@declarative_mixin
class SomethingMixin:
    @declared_attr
    def dprop(cls):
        return deferred(Column(Integer))


class SomethingModel(SomethingMixin, Base):
    __tablename__ = "something"
    
    id = Column(Integer, primary_key=True)


@declarative_mixin
class AdditionalMixin:
    x = Column(Integer)
    y = Column(Integer)
    
    @declared_attr
    def x_plus_y(cls):
        return column_property(cls.x + cls.y)
