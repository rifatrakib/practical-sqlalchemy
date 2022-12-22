from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import INET, CIDR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class IPA(Base):
    __tablename__ = "ip_address"
    
    id = Column(Integer, primary_key=True)
    v4address = Column(INET)
    
    network = relationship(
        "Network",
        primaryjoin="IPA.v4address.bool_op('<<')" "(foreign(Network.v4representation))",
        viewonly=True,
    )


class Network(Base):
    __tablename__ = "network"
    
    id = Column(Integer, primary_key=True)
    v4representation = Column(CIDR)
