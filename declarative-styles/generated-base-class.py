from sqlalchemy.orm import registry, declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String

reg = registry()
Base = reg.generate_base()

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)
