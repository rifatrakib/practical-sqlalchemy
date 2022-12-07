from sqlalchemy import Column, Integer, Table
from sqlalchemy.orm import declarative_base, composite, registry

Base = declarative_base()
mapper_registry = registry()


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __composite_values__(self):
        return self.x, self.y
    
    def __repr__(self):
        return f"Point(x={self.x!r}, y={self.y!r})"
    
    def __eq__(self, other):
        return isinstance(other, Point) and other.x == self.x and other.y == self.y
    
    def __ne__(self, other):
        return not self.__eq__(other)


class Vertex(Base):
    __tablename__ = "vertices"
    
    id = Column(Integer, primary_key=True)
    x1 = Column(Integer)
    y1 = Column(Integer)
    x2 = Column(Integer)
    y2 = Column(Integer)
    
    start = composite(Point, x1, y1)
    end = composite(Point, x2, y2)


class VertexMapper:
    pass


vertices_table = Table(
    "vertices_table",
    Base.metadata,
    Column("x1", Integer),
    Column("y1", Integer),
    Column("x2", Integer),
    Column("y2", Integer),
)

mapper_registry.map_imperatively(
    VertexMapper,
    vertices_table,
    properties={
        "start": composite(Point, vertices_table.c.x1, vertices_table.c.y1),
        "end": composite(Point, vertices_table.c.x2, vertices_table.c.y2),
    }
)
