from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class A(Base):
    __tablename__ = "a"
    
    id = Column(Integer, primary_key=True)
    b_id = Column(ForeignKey("b.id"))
    
    d = relationship(
        "D",
        secondary="join(B, D, B.d_id == D.id)." "join(C, C.d_id == D.id)",
        primaryjoin="and_(A.b_id == B.id, A.id == C.a_id)",
        secondaryjoin="D.id == B.d_id",
        uselist=False,
        viewonly=True,
    )


class B(Base):
    __tablename__ = "b"
    
    id = Column(Integer, primary_key=True)
    d_id = Column(ForeignKey("d.id"))


class C(Base):
    __tablename__ = "c"
    
    id = Column(Integer, primary_key=True)
    a_id = Column(ForeignKey("a.id"))
    d_id = Column(ForeignKey("d.id"))


class D(Base):
    __tablename__ = "d"
    id = Column(Integer, primary_key=True)
