from sqlalchemy import Column, Integer, sql
from sqlalchemy.orm import CompositeProperty, declarative_base, composite

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


class PointComparator(CompositeProperty.Comparator):
    def __gt__(self, other):
        """redefine the 'greater than' operation"""
        return sql.and_(
            *[
                a > b for a, b in zip(
                    self.__clause_element__().clauses,
                    other.__composite_values__(),
                )
            ]
        )


class Vertex(Base):
    __tablename__ = "vertices"
    
    id = Column(Integer, primary_key=True)
    x1 = Column(Integer)
    y1 = Column(Integer)
    x2 = Column(Integer)
    y2 = Column(Integer)
    
    start = composite(Point, x1, y1, comparator_factory=PointComparator)
    end = composite(Point, x2, y2, comparator_factory=PointComparator)
