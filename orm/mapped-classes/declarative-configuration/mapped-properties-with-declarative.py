from sqlalchemy import Column, ForeignKey, Integer, String, Text, Table
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


class HybridUser(Base):
    __table__ = Table(
        "hybrid_user",
        Base.metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("firstname", String(50)),
        Column("lastname", String(50)),
    )
    
    fullname = column_property(__table__.c.firstname + " " + __table__.c.lastname)
    
    addresses = relationship("HybridAddress", back_populates="user")


class HybridAddress(Base):
    __table__ = Table(
        "hybrid_address",
        Base.metadata,
        Column("id", Integer, primary_key=True),
        Column("user_id", ForeignKey("user.id")),
        Column("email_address", String),
        Column("address_statistics", Text),
    )
    
    address_statistics = deferred(__table__.c.address_statistics)
    
    user = relationship("HybridUser", back_populates="addresses")
