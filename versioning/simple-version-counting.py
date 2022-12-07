from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    version_id = Column(Integer, nullable=False)
    name = Column(String(50), nullable=False)
    
    __mapper_args__ = {"version_id_col": version_id}
