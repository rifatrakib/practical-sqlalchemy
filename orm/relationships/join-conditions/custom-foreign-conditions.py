from sqlalchemy import cast, String, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship, foreign, remote

Base = declarative_base()


class HostEntry(Base):
    __tablename__ = "host_entry"
    
    id = Column(Integer, primary_key=True)
    ip_address = Column(INET)
    content = Column(String(50))
    
    # relationship() using explicit foreign_keys, remote_side
    parent_host = relationship(
        "HostEntry",
        primaryjoin=ip_address == cast(content, INET),
        foreign_keys=content,
        remote_side=ip_address,
    )


class SuccinctHostEntry(Base):
    __tablename__ = "succinct_host_entry"
    
    id = Column(Integer, primary_key=True)
    ip_address = Column(INET)
    content = Column(String(50))
    
    # relationship() using explicit foreign() and remote() annotations
    # in lieu of separate arguments
    parent_host = relationship(
        "SuccinctHostEntry",
        primaryjoin=remote(ip_address) == cast(foreign(content), INET),
    )
