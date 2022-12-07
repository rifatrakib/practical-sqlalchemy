from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    version_uuid = Column(String(32), nullable=False)
    name = Column(String(50), nullable=False)
    
    __mapper_args__ = {
        "version_id_col": version_uuid,
        "version_id_generator": lambda version: uuid.uuid4().hex,
    }
