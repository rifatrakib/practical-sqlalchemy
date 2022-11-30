from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, validates, relationship

Base = declarative_base()


class EmailAddress(Base):
    __tablename__ = "address"
    
    id = Column(Integer, primary_key=True)
    email = Column(String)
    
    @validates("email")
    def validate_email(self, key, address):
        if "@" not in address.email:
            raise ValueError("failed simplified email validation")
        return address


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String)
    
    addresses = relationship("Address")
    
    @validates("addresses")
    def validate_addresses(self, key, address):
        if "@" not in address.email:
            raise ValueError("failed simplified email validation")
        return address


class UserRedundant(Base):
    __tablename__ = "user_redundant"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String)
    
    addresses = relationship("Address")
    
    @validates("addresses", include_removes=True)
    def validate_addresses(self, key, address):
        if "@" not in address.email:
            raise ValueError("failed simplified email validation")
        return address


class Address(Base):
    __tablename__ = "address_backref"
    
    id = Column(Integer, primary_key=True)
    email = Column(String)
    user_id = Column(Integer, ForeignKey("user_backref.id"), nullable=False)
    
    @validates("email")
    def validate_email(self, key, address):
        if "@" not in address.email:
            raise ValueError("failed simplified email validation")
        return address


class UserBackref(Base):
    __tablename__ = "user_backref"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String)
    
    addresses = relationship("Address", backref="user")
    
    @validates("addresses", include_backrefs=False)
    def validate_addresses(self, key, address):
        if "@" not in address.email:
            raise ValueError("failed simplified email validation")
        return address
