from sqlalchemy import Column, ForeignKey, Integer, String, select, func
from sqlalchemy.orm import declarative_base, object_session

Base = declarative_base()


class Address(Base):
    __tablename__ = "address"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    
    @property
    def address_count(self):
        return object_session(self).scalar(
            select(func.count(Address.id)).
            where(Address.user_id == self.id)
        )
