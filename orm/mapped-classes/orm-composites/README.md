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


#### Tracking In-Place Mutations on Composites

_In-place changes_ to an _existing composite value_ are __not tracked automatically__. Instead, the _composite class_ needs to _provide events_ to its parent object __explicitly__. This task is _largely automated_ via the usage of the `MutableComposite` mixin, which _uses events to associate each user-defined composite object with all parent associations_.


#### Redefining Comparison Operations for Composites

The `"equals"` comparison operation _by default_ produces an __AND__ of all corresponding columns equated to one another. This can be changed using the `comparator_factory` argument to `composite()`, where we specify a _custom_ `Comparator` class to __define existing or new operations__. Below we illustrate the `"greater than"` operator, implementing the same expression that the base `"greater than"` does.

```
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
```


#### Nesting Composites

_Composite objects_ can be defined to work in _simple nested schemes_, by __redefining behaviors within the composite class__ to work as desired, then _mapping the composite class_ to the _full length of individual columns_ normally. Typically, it is convenient to _define separate constructors for user-defined use and generate-from-row use_. Below we reorganize the `Vertex` class to itself be a _composite object_, which is then mapped to a class `HasVertex`.

```
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
```

We can then use the above mapping as:

```
hv = HasVertex(vertex=Vertex(Point(1, 2), Point(3, 4)))

s.add(hv)
s.commit()

hv = (
    s.query(HasVertex)
    .filter(HasVertex.vertex == Vertex(Point(1, 2), Point(3, 4)))
    .first()
)
print(hv.vertex.start)
print(hv.vertex.end)
```
