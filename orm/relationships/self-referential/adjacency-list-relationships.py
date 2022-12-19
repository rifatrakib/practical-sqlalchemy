from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import backref, declarative_base, relationship

Base = declarative_base()


class Node(Base):
    __tablename__ = "node"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("node.id"))
    data = Column(String(50))
    children = relationship("Node")


class NodeRemote(Base):
    __tablename__ = "node_remote"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("node_remote.id"))
    data = Column(String(50))
    parent = relationship("NodeRemote", remote_side=[id])


class NodeBidirect(Base):
    __tablename__ = "node_bidirect"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("node_bidirect.id"))
    data = Column(String(50))
    children = relationship("NodeBidirect", backref=backref("parent", remote_side=[id]))
