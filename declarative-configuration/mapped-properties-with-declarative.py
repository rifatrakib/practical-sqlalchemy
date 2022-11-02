from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import (
    column_property, declarative_base, deferred, relationship,
)

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    firstname = Column(String(50))
    lastname = Column(String(50))
    
    fullname = column_property(firstname + " " + lastname)
    
    addresses = relationship("Address", back_populates="user")


class Address(Base):
    __tablename__ = "address"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("user.id"))
    email_address = Column(String)
    
    address_statistics = deferred(Column(Text))
    
    user = relationship("User", back_populates="addresses")
