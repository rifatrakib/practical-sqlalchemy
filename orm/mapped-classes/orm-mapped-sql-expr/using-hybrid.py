from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import case
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    
    @hybrid_property
    def fullname(self):
        return f"{self.firstname} {self.lastname}"


class UpgradedUser(Base):
    __tablename__ = "upgraded_user"
    
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    
    @hybrid_property
    def fullname(self):
        if self.firstname is not None:
            return f"{self.firstname} {self.lastname}"
        else:
            return self.lastname
    
    @fullname.expression
    def fullname(cls):
        return case(
            [(cls.firstname != None, f"{cls.firstname} {cls.lastname}")],
            else_=cls.lastname,
        )
