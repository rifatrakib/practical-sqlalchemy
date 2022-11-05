from sqlalchemy import Column, String, Integer, DateTime, select
from sqlalchemy.orm import declared_attr, declarative_base
from datetime import datetime

Base = declarative_base()


class GroupUsers(Base):
    __tablename__ = "group_users"
    
    user_id = Column(String(40))
    group_id = Column(String(40))
    
    __mapper_args__ = {"primary_key": [user_id, group_id]}


class Widget(Base):
    __tablename__ = "widgets"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    
    __mapper_args__ = {
        "version_id_col": timestamp,
        "version_id_generator": lambda v: datetime.now(),
    }


class Person(Base):
    __tablename__ = "person"
    
    person_id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    
    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "person",
    }


class Employee(Person):
    __mapper_args__ = {
        "polymorphic_identity": "employee",
    }


class ExcludeColsWFlag:
    @declared_attr
    def __mapper_args__(cls):
        return {
            "exclude_properties": [
                column.key for column in cls.__table__.c
                if column.info.get("exclude", False)
            ]
        }


class Data(ExcludeColsWFlag, Base):
    __tablename__ = "data"
    
    id = Column(Integer, primary_key=True)
    data = Column(String)
    
    not_needed = Column(String, info={"exclude": True})
