from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import registry, relationship

mapper_registry = registry()


@mapper_registry.mapped
class User:
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    addresses = relationship("Address", back_populates="user")


@mapper_registry.mapped
class Address:
    __tablename__ = "address"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("user.id"))
    email_address = Column(String)
    
    user = relationship("User", back_populates="addresses")


@mapper_registry.mapped
class Person:
    __tablename__ = "person"
    
    person_id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    
    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "person",
    }


@mapper_registry.mapped
class Employee:
    __tablename__ = "employee"
    
    person_id = Column(Integer, ForeignKey("person.person_id"), primary_key=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "employee",
    }
