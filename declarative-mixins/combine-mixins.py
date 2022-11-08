from sqlalchemy import Column, Integer
from sqlalchemy.orm import declared_attr, declarative_mixin, declarative_base

Base = declarative_base()


@declarative_mixin
class MySQLMixin:
    __table_args__ = {"mysql_engine": "InnoDB"}


@declarative_mixin
class InfoMixin:
    __table_args__ = {"info": "foo"}


class DatabaseModel(MySQLMixin, InfoMixin, Base):
    __tablename__ = "table"
    
    @declared_attr
    def __table_args__(cls):
        args = dict()
        args.update(MySQLMixin.__table_args__)
        args.update(InfoMixin.__table_args__)
        return args
    
    id = Column(Integer, primary_key=True)
