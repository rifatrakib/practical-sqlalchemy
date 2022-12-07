from sqlalchemy import Column, FetchedValue, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    xmin = Column("xmin", String, system=True, server_default=FetchedValue())
    
    __mapper_args__ = {"version_id_col": xmin, "version_id_generator": False}
