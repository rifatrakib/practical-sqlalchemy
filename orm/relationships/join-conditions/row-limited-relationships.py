from sqlalchemy import Column, ForeignKey, Integer, func, select, and_
from sqlalchemy.orm import aliased, declarative_base, relationship

Base = declarative_base()


class A(Base):
    __tablename__ = "a"
    id = Column(Integer, primary_key=True)


class B(Base):
    __tablename__ = "b"
    id = Column(Integer, primary_key=True)
    a_id = Column(ForeignKey("a.id"))


partition = select(
    B, func.row_number().over(order_by=B.id, partition_by=B.a_id).label("index")
).alias()

partitioned_b = aliased(B, partition)

A.partitioned_bs = relationship(
    partitioned_b, primaryjoin=and_(partitioned_b.a_id == A.id, partition.c.index < 10)
)
