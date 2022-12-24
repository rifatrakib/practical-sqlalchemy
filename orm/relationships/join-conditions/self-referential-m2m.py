from sqlalchemy import Column, Integer, ForeignKey, MetaData, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import registry, relationship

Base = declarative_base()
metadata_obj = MetaData()
mapper_registry = registry()

node_to_node = Table(
    "node_to_node",
    Base.metadata,
    Column("left_node_id", Integer, ForeignKey("node.id"), primary_key=True),
    Column("right_node_id", Integer, ForeignKey("node.id"), primary_key=True),
)

node_to_node_meta = Table(
    "node_to_node_meta",
    metadata_obj,
    Column("left_node_id", Integer, ForeignKey("node.id"), primary_key=True),
    Column("right_node_id", Integer, ForeignKey("node.id"), primary_key=True),
)

node_var = Table(
    "node_var",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("label", String),
)


class NodeObject(Base):
    __tablename__ = "node_object"
    id = Column(Integer, primary_key=True)
    label = Column(String)
    right_nodes = relationship(
        "NodeObject",
        secondary=node_to_node,
        primaryjoin=id == node_to_node.c.left_node_id,
        secondaryjoin=id == node_to_node.c.right_node_id,
        backref="left_nodes",
    )


class NodeString(Base):
    __tablename__ = "node_string"
    id = Column(Integer, primary_key=True)
    label = Column(String)
    right_nodes = relationship(
        "NodeString",
        secondary="node_to_node",
        primaryjoin="NodeString.id==node_to_node.c.left_node_id",
        secondaryjoin="NodeString.id==node_to_node.c.right_node_id",
        backref="left_nodes",
    )


class NodeVar(object):
    pass


mapper_registry.map_imperatively(
    NodeVar,
    node_var,
    properties={
        "right_nodes": relationship(
            NodeVar,
            secondary=node_to_node_meta,
            primaryjoin=node_var.c.id == node_to_node_meta.c.left_node_id,
            secondaryjoin=node_var.c.id == node_to_node_meta.c.right_node_id,
            backref="left_nodes",
        )
    },
)
