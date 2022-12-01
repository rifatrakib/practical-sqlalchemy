## Composite Column Types

_Sets of columns_ __can be associated__ with a _single user-defined datatype_. The ORM provides a _single attribute_ which __represents the group of columns__ using the class you provide.

A simple example represents pairs of columns as a `Point` object. `Point` represents such a pair as _.x_ and _.y_.

```
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
```

The requirements for the _custom datatype class_ are that it have a `constructor` which __accepts positional arguments corresponding to its column format__, and also provides a method `__composite_values__()` which returns the state of the object as a _list_ or _tuple_, in order of its _column-based attributes_. It also should supply adequate `__eq__()` and `__ne__()` methods which test the equality of two instances.

We will create a mapping to a table _vertices_, which __represents two points__ as `x1/y1` and `x2/y2`. These are created normally as `Column` objects. Then, the `composite()` function is used to __assign new attributes__ that will _represent sets of columns_ via the `Point` class.

```
class Vertex(Base):
    __tablename__ = "vertices"
    
    id = Column(Integer, primary_key=True)
    x1 = Column(Integer)
    y1 = Column(Integer)
    x2 = Column(Integer)
    y2 = Column(Integer)
    
    start = composite(Point, x1, y1)
    end = composite(Point, x2, y2)
```

A _classical mapping_ above would define each `composite()` against the existing table.

```
mapper_registry.map_imperatively(
    VertexMapper,
    vertices_table,
    properties={
        "start": composite(Point, vertices_table.c.x1, vertices_table.c.y1),
        "end": composite(Point, vertices_table.c.x2, vertices_table.c.y2),
    }
)
```

We can now _persist_ and use `Vertex` instances, as well as query for them, using the `.start` and `.end` attributes against _ad-hoc_ `Point` instances.

```
v = Vertex(start=Point(3, 4), end=Point(5, 6))
session.add(v)
q = session.query(Vertex).filter(Vertex.start == Point(3, 4))
print(q.first().start)
```