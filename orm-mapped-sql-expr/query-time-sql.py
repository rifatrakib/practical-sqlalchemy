from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base, query_expression

Base = declarative_base()


class A(Base):
    __tablename__ = "a"
    
    id = Column(Integer, primary_key=True)
    x = Column(Integer)
    y = Column(Integer)
    
    expr = query_expression()
