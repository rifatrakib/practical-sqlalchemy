from sqlalchemy import Column, ForeignKey, Integer, String, join, select
from sqlalchemy.orm import aliased, declarative_base, relationship

Base = declarative_base()


class A(Base):
    __tablename__ = "a"
    id = Column(Integer, primary_key=True)
    b_id = Column(ForeignKey("b.id"))


class B(Base):
    __tablename__ = "b"
    id = Column(Integer, primary_key=True)


class C(Base):
    __tablename__ = "c"
    id = Column(Integer, primary_key=True)
    a_id = Column(ForeignKey("a.id"))
    some_c_value = Column(String)


class D(Base):
    __tablename__ = "d"
    id = Column(Integer, primary_key=True)
    c_id = Column(ForeignKey("c.id"))
    b_id = Column(ForeignKey("b.id"))
    some_d_value = Column(String)


# 1. set up the join() as a variable, so we can refer
# to it in the mapping multiple times.
j = join(B, D, D.b_id == B.id).join(C, C.id == D.c_id)

# 2. Create an AliasedClass to B
B_viacd = aliased(B, j, flat=True)

A.b = relationship(B_viacd, primaryjoin=A.b_id == j.c.b_id)

subq = select(B).join(D, D.b_id == B.id).join(C, C.id == D.c_id).subquery()
B_viacd_subquery = aliased(B, subq)
A.b = relationship(B_viacd_subquery, primaryjoin=A.b_id == subq.c.id)
