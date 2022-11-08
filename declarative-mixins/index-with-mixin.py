from sqlalchemy import Column, Integer, Index
from sqlalchemy.orm import declared_attr, declarative_base, declarative_mixin

Base = declarative_base()


@declarative_mixin
class IndexMixin:
    a = Column(Integer)
    b = Column(Integer)
    
    @declared_attr
    def __table_args__(cls):
        return (Index(f"test_idx_{cls.__tablename__}", "a", "b"), )


class MyModel(IndexMixin, Base):
    __tablename__ = "atable"
    
    c = Column(Integer, primary_key=True)
