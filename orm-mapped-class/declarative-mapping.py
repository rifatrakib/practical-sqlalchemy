from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import registry, declarative_base

# declarative base class
Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)


# equivalent to Base = declarative_base()
mapper_registry = registry()
Base = mapper_registry.generate_base()
