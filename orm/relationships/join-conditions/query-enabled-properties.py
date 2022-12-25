from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base, object_session

Base = declarative_base()


class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    
    @property
    def addresses(self):
        return object_session(self).query(Address).with_parent(self).filter(...).all()
