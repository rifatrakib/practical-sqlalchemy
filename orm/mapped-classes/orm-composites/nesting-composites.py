from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base, composite

Base = declarative_base()


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


class Vertex:
    def __init__(self, start, end):
        self.start = start
        self.end = end
    
    @classmethod
    def _generate(cls, x1, y1, x2, y2):
        """generate a Vertex from a row"""
        return Vertex(Point(x1, x2), Point(x2, y2))
    
    def __composite_values__(self):
        return self.start.__composite_values__() + self.end.__composite_values__()


class HasVertex(Base):
    __tablename__ = "has_vertex"
    
    id = Column(Integer, primary_key=True)
    x1 = Column(Integer)
    y1 = Column(Integer)
    x2 = Column(Integer)
    y2 = Column(Integer)
    
    vertex = composite(Vertex._generate, x1, y1, x2, y2)
