from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import declared_attr, declarative_base, declarative_mixin

Base = declarative_base()


@declarative_mixin
class TimestampMixin:
    created_at = Column(DateTime, default=func.now())


@declarative_mixin
class ReferenceAddressMixin:
    @declared_attr
    def address_id(cls):
        return Column(Integer, ForeignKey("address.id"))


@declarative_mixin
class MyMixin:
    @declared_attr
    def type_(cls):
        return Column(String(50))
    
    __mapper_args__ = {"polymorphic_on": type_}


class MyModel(TimestampMixin, Base):
    __tablename__ = "test"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(1000))


class User(ReferenceAddressMixin, Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)


class PolymorphicModel(MyMixin, Base):
    __tablename__ = "polymorphic_table"
    id = Column(Integer, primary_key=True)
