## Mapping Class Inheritance Hierarchies

SQLAlchemy supports _three forms of inheritance_: `single table inheritance`, where _several_ types of classes are __represented by a single table__, `concrete table inheritance`, where _each_ type of class is __represented by independent tables__, and `joined table inheritance`, where the _class hierarchy_ is __broken up among dependent tables__, each class represented by its own table that only includes those attributes local to that class.

The _most common_ forms of inheritance are _single and joined table_, while _concrete inheritance_ presents __more configurational challenges__.

_When mappers are configured_ in an `inheritance relationship`, SQLAlchemy has the ability to __load elements polymorphically__, meaning that a _single query_ can return objects of __multiple types__.


#### Joined Table Inheritance

In _joined table inheritance_, each class along a __hierarchy of classes__ is represented by a _distinct table_. _Querying for a particular subclass_ in the hierarchy will __render as a `SQL JOIN` along all tables in its inheritance path__. If the queried class is the _base class_, the _default behavior_ is to __include only the base table__ in a SELECT statement. In all cases, the ultimate _class to instantiate_ for a given row is determined by a __discriminator column__ or __an expression that works against the base table__. When a subclass is loaded only against a base table, resulting objects will have __base attributes populated at first__; _attributes that are local to the subclass_ will __lazy load__ when they are accessed. Alternatively, there are _options_ which can _change the default behavior_, allowing the query to include columns corresponding to multiple tables/subclasses up front.

The _base class_ in a `joined inheritance hierarchy` is configured with additional arguments that will refer to the __polymorphic discriminator column__ as well as the identifier for the base class.

```
class Employee(Base):
    __tablename__ = "employee"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(50))
    
    __mapper_args__ = {
        "polymorphic_identity": "employee",
        "polymorphic_on": type,
    }
```

Above, an additional column _type_ is established to act as the __discriminator__, configured as such using the `mapper.polymorphic_on` parameter. This column will store a value which _indicates the type of object represented within the row_. The column may be of __any datatype__, though _string_ and _integer_ are the _most common_. The actual data value to be applied to this column for a particular row in the database is specified using the `mapper.polymorphic_identity` parameter, described below.

While a _polymorphic discriminator expression_ is __not strictly necessary__, it is _required if polymorphic loading is desired_. Establishing a simple column on the base table is the easiest way to achieve this, however _very sophisticated inheritance mappings_ may even __configure a SQL expression__ such as a `CASE` statement as the _polymorphic discriminator_.

> ##### Note
>
> Currently, __only one discriminator column or SQL expression__ may be configured for the _entire inheritance hierarchy_, typically on the _base-most class_ in the hierarchy. `"Cascading"` _polymorphic discriminator expressions_ are __not yet supported__.

We next define _Engineer_ and _Manager_ subclasses of _Employee_. Each contains columns that represent the _attributes unique to the subclass_ they represent. Each table also __must contain a primary key column__ (or columns), as well as a __foreign key reference to the parent table__.

```
class Engineer(Base):
    __tablename__ = "engineer"
    
    id = Column(Integer, ForeignKey("employee.id"), primary_key=True)
    engineer_name = Column(String(30))
    
    __mapper_args__ = {
        "polymorphic_identity": "engineer",
    }


class Manager(Base):
    __tablename__ = "manager"
    
    id = Column(Integer, ForeignKey("employee.id"), primary_key=True)
    manager_name = Column(String(30))
    
    __mapper_args__ = {
        "polymorphic_identity": "manager",
    }
```

In the above example, each mapping specifies the `mapper.polymorphic_identity` parameter within its mapper arguments. This value populates the column designated by the `mapper.polymorphic_on` parameter _established on the base mapper_. The `mapper.polymorphic_identity` parameter should be __unique to each mapped class across the whole hierarchy__, and there should only be __one "identity" per mapped class__; as noted above, `"cascading" identities` where some subclasses introduce a second identity are __not supported__.

The ORM uses the value set up by `mapper.polymorphic_identity` in order to __determine which class a row belongs__ towards when _loading rows polymorphically_. In the example above, every row which represents an _Employee_ will have the value _'employee'_ in its `type` row; similarly, every _Engineer_ will get the value _'engineer'_, and each _Manager_ will get the value _'manager'_. _Regardless_ of whether the _inheritance mapping_ uses _distinct joined tables for subclasses_ as in `joined table inheritance`, or _all one table_ as in `single table inheritance`, this value is __expected to be persisted and available to the ORM when querying__. The `mapper.polymorphic_identity` parameter __also applies__ to `concrete table inheritance`, but is __not actually persisted__; see the later section at `Concrete Table Inheritance` for details.

In a _polymorphic setup_, it is _most common_ that the `foreign key constraint` is established on the __same column or columns as the primary key itself__, however this is __not required__; a _column distinct from the primary key_ may also be made to _refer to the parent via foreign key_. The way that a `JOIN` is _constructed from the base table to subclasses_ is also __directly customizable__, however this is _rarely necessary_.

> ##### Joined inheritance primary keys
>
> One _natural effect_ of the `joined table inheritance` configuration is that the _identity of any mapped object_ can be __determined entirely from rows in the base table alone__. This has obvious _advantages_, so _SQLAlchemy_ __always considers__ the _primary key columns of a joined inheritance class_ to be those of the __base table only__. In other words, the _id_ columns of both the _engineer_ and _manager_ tables are __not used to locate__ _Engineer_ or _Manager_ objects - only the value in _employee.id_ is considered. _engineer.id_ and _manager.id_ are still of course __critical to the proper operation of the pattern overall__ as they are used to _locate the joined row_, once the _parent row_ __has been determined__ within a statement.

With the `joined inheritance mapping` complete, querying against _Employee_ will return a _combination of Employee, Engineer and Manager objects_. Newly saved _Engineer_, _Manager_, and _Employee_ objects will __automatically populate__ the `employee.type` column with the correct `"discriminator"` value in this case _"engineer"_, _"manager"_, or _"employee"_, as appropriate.


##### Relationships with Joined Inheritance

_Relationships_ are __fully supported__ with `joined table inheritance`. The relationship involving a _joined-inheritance class should target the class in the hierarchy_ that also __corresponds to the foreign key constraint__; below, as the _employee table_ has a `foreign key constraint` back to the _company table_, the _relationships are set up_ between _Company_ and _Employee_.

```
class Company(Base):
    __tablename__ = "company"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    employees = relationship("Employee", back_populates="company")


class Employee(Base):
    __tablename__ = "employee"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(50))
    
    company_id = Column(ForeignKey("company.id"))
    company = relationship("Company", back_populates="employees")
    
    __mapper_args__ = {
        "polymorphic_identity": "employee",
        "polymorphic_on": type,
    }
```

If the `foreign key constraint` is on a table corresponding to a subclass, the _relationship_ should __target that subclass instead__. In the example below, there is a `foreign key constraint` _from manager to company_, so the _relationships_ are established between the _Manager_ and _Company_ classes.

Above, the _Manager_ class will have a _Manager.company_ attribute; _Company_ will have a _Company.managers_ attribute that always loads against a join of the employee and manager tables together.


##### Loading Joined Inheritance Mappings

See the sections `Loading Inheritance Hierarchies` and `Loading objects with joined table inheritance` for background on _inheritance loading techniques_, including _configuration_ of tables to be queried both at _mapper configuration time_ as well as _query time_.
