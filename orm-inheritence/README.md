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


#### Single Table Inheritance

`Single table inheritance` represents _all attributes of all subclasses_ __within a single table__. A particular _subclass_ that has __attributes unique to that class__ will _persist them within columns_ in the table that are otherwise `NULL` if the row refers to a different kind of object.

__Querying__ for a particular _subclass_ in the hierarchy will render as a `SELECT` _against the base table_, which will include a `WHERE` clause that _limits rows_ to those with a particular value or values present in the __discriminator column or expression__.

`Single table inheritance` has the __advantage of simplicity__ compared to _joined table inheritance_; _queries_ are __much more efficient__ as only one table needs to be involved in order to load objects of every represented class.

_Single table inheritance configuration_ looks much like `joined-table inheritance`, except only the _base class_ specifies `__tablename__`. A _discriminator column_ is also __required on the base table__ so that _classes can be differentiated from each other_.

Even though _subclasses share the base table for all of their attributes_, when using _Declarative_, `Column` objects __may still be specified on subclasses__, indicating that the _column_ is to be __mapped only to that subclass__; the `Column` will be applied to the __same base `Table` object__.

```
class Employee(Base):
    __tablename__ = "employee"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(20))
    
    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "employee",
    }


class Manager(Employee):
    manager_data = Column(String(50))
    
    __mapper_args__ = {
        "polymorphic_identity": "manager",
    }


class Engineer(Employee):
    engineer_data = Column(String(50))
    
    __mapper_args__ = {
        "polymorphic_identity": "engineer",
    }
```

Note that the _mappers for the derived classes_ `Manager` and `Engineer` __omit the `__tablename__`__, indicating they __do not have a mapped table of their own__.


##### Resolving Column Conflicts

Note in the previous section that the *manager_name* and *engineer_info* columns are __"moved up"__ to be applied to `Employee.__table__`, as a result of their _declaration on a subclass that has no table of its own_. A _tricky case_ comes up when _two subclasses want to specify the same column_.

```
class Manager(Employee):
    manager_data = Column(String(50))
    start_date = Column(DateTime)
    
    __mapper_args__ = {
        "polymorphic_identity": "manager",
    }


class Engineer(Employee):
    engineer_data = Column(String(50))
    start_date = Column(DateTime)
    
    __mapper_args__ = {
        "polymorphic_identity": "engineer",
    }
```

Above, the `start_date` column declared on both _Engineer_ and _Manager_ will result in an error:

```
sqlalchemy.exc.ArgumentError: Column 'start_date' on class
<class '__main__.Manager'> conflicts with existing
column 'employee.start_date'
```

The above scenario presents an _ambiguity_ to the _Declarative mapping system_ that may be __resolved__ by using `declared_attr` to __define the `Column` conditionally__, taking care to return the existing column via the parent `__table__` if it already exists.

```
class Manager(Employee):
    __mapper_args__ = {
        "polymorphic_identity": "manager",
    }
    
    @declared_attr
    def start_date(cls):
        """Start date column, if not present already"""
        return Employee.__table__.c.get("start_date", Column(DateTime))


class Engineer(Employee):
    __mapper_args__ = {
        "polymorphic_identity": "engineer",
    }
    
    @declared_attr
    def start_date(cls):
        """Start date column, if not present already"""
        return Employee.__table__.c.get("start_date", Column(DateTime))
```

Above, when _Manager_ is mapped, the `start_date` column is _already present_ on the _Employee_ class; by returning the existing Column object, the _declarative system_ recognizes that this is the __same column to be mapped to the two different subclasses separately__.

A _similar concept_ can be used with _mixin classes_ (see `Composing Mapped Hierarchies with Mixins`) to define a _particular series of columns and/or other mapped attributes_ from a __reusable mixin class__.

```
class Employee(Base):
    __tablename__ = "employee"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(20))

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "employee",
    }


class HasStartDate:
    @declared_attr
    def start_date(cls):
        return cls.__table__.c.get("start_date", Column(DateTime))


class Engineer(HasStartDate, Employee):
    __mapper_args__ = {
        "polymorphic_identity": "engineer",
    }


class Manager(HasStartDate, Employee):
    __mapper_args__ = {
        "polymorphic_identity": "manager",
    }
```


##### Relationships with Single Table Inheritance

_Relationships_ are __fully supported__ with `single table inheritance`. _Configuration_ is done in the __same manner__ as that of `joined inheritance`; a _foreign key attribute_ should be __on the same class__ that's the __"foreign" side of the relationship__.

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


class Manager(Employee):
    manager_data = Column(String(50))

    __mapper_args__ = {
        "polymorphic_identity": "manager",
    }


class Engineer(Employee):
    engineer_info = Column(String(50))

    __mapper_args__ = {
        "polymorphic_identity": "engineer",
    }
```

Also, like the case of _joined inheritance_, we can create `relationships` that involve a specific subclass. When queried, the `SELECT` statement will include a `WHERE` clause that __limits the class selection to that subclass or subclasses__.

```
class Company(Base):
    __tablename__ = "company"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    managers = relationship("Manager", back_populates="company")


class Employee(Base):
    __tablename__ = "employee"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(50))

    __mapper_args__ = {
        "polymorphic_identity": "employee",
        "polymorphic_on": type,
    }


class Manager(Employee):
    manager_name = Column(String(30))

    company_id = Column(ForeignKey("company.id"))
    company = relationship("Company", back_populates="managers")

    __mapper_args__ = {
        "polymorphic_identity": "manager",
    }


class Engineer(Employee):
    engineer_info = Column(String(50))

    __mapper_args__ = {
        "polymorphic_identity": "engineer",
    }
```

Above, the _Manager_ class will have a `Manager.company` attribute; _Company_ will have a `Company.managers` attribute that __always loads against the employee__ with an _additional_ `WHERE` clause that __limits rows__ to those with `type = 'manager'`.


##### Loading Single Inheritance Mappings

The _loading techniques_ for `single-table inheritance` are __mostly identical__ to those used for _joined-table inheritance_, and a _high degree of abstraction_ is provided between these two mapping types such that it is __easy to switch__ between them as well as to __intermix__ them in a _single hierarchy_ (just __omit `__tablename__` from whichever subclasses are to be single-inheriting__). See the sections `Loading Inheritance Hierarchies` and `Loading objects with single table inheritance` for documentation on inheritance loading techniques, including configuration of classes to be queried both at mapper configuration time as well as query time.


#### Concrete Table Inheritance

`Concrete inheritance` __maps each subclass to its own distinct table__, each of which contains __all columns necessary__ to produce an instance of that class. A _concrete inheritance configuration_ by default __queries non-polymorphically__; a query for a particular class will only query that class' table and only return instances of that class. _Polymorphic loading of concrete classes_ is enabled by __configuring within the mapper__ a _special_ `SELECT` that typically is produced as a `UNION` of _all the tables_.

> ##### Warning
>
> _Concrete table inheritance_ is __much more complicated__ than _joined or single table inheritance_, and is __much more limited in functionality__ especially pertaining to _using it with relationships_, `eager loading`, and `polymorphic loading`. When used _polymorphically_ it produces _very large queries with UNIONS_ that __won't perform as well as simple joins__. It is strongly advised that if _flexibility_ in `relationship loading` and `polymorphic loading` is required, that _joined or single table inheritance_ be used if at all possible. If `polymorphic loading` isn't required, then _plain non-inheriting mappings_ can be used if each class refers to its own table completely.

Whereas _joined and single table inheritance_ are __fluent__ in `"polymorphic" loading`, it is a _more awkward affair_ in `concrete inheritance`. For this reason, _concrete inheritance_ is __more appropriate__ when __polymorphic loading is not required__. Establishing relationships that involve concrete inheritance classes is also more awkward.

To establish a class as using _concrete inheritance_, add the `mapper.concrete` parameter within the `__mapper_args__`. This indicates to _Declarative_ as well as the mapping that the _superclass table_ __should not be considered as part of the mapping__.

_Two critical points_ should be noted:

* We must __define all columns explicitly__ on _each subclass_, even those of the same name. A column such as `Employee.name` here is __not copied out__ to the tables mapped by _Manager_ or _Engineer_ for us.

* while the _Engineer_ and _Manager_ classes are _mapped in an inheritance relationship_ with _Employee_, they still __do not include polymorphic loading__. Meaning, if we query for _Employee_ objects, the _manager_ and _engineer_ tables are __not queried at all__.


##### Concrete Polymorphic Loading Configuration

_Polymorphic loading with concrete inheritance_ requires that a _specialized_ `SELECT` is __configured against each base class that should have polymorphic loading__. This `SELECT` needs to be __capable of accessing all the mapped tables individually__, and is typically a `UNION` statement that is constructed using a SQLAlchemy helper `polymorphic_union()`.

As discussed in `Loading Inheritance Hierarchies`, _mapper inheritance configurations_ of any type __can be configured__ to _load from a special selectable_ by default using the `mapper.with_polymorphic` argument. Current public API requires that this argument is set on a _Mapper_ when it is first constructed.

However, in the case of _Declarative_, both the _mapper_ and the _Table that is mapped_ are __created at once__, the moment the mapped class is defined. This means that the `mapper.with_polymorphic` argument __cannot be provided yet__, since the _Table_ objects that correspond to the subclasses _haven't yet been defined_.

There are a few strategies available to resolve this cycle, however _Declarative_ provides _helper classes_ `ConcreteBase` and `AbstractConcreteBase` which handle this issue behind the scenes.

Using `ConcreteBase`, we can set up our concrete mapping in almost the same way as we do other forms of inheritance mappings.

Above, _Declarative_ sets up the __polymorphic selectable__ for the _Employee_ class at __mapper `"initialization"` time__; this is the _late-configuration step_ for mappers that __resolves__ other _dependent mappers_. The `ConcreteBase` helper uses the `polymorphic_union()` function to _create a UNION of all concrete-mapped tables_ after all the other classes are set up, and then _configures_ this statement with the __already existing base-class mapper__.

Upon _select_, the `polymorphic union` produces a query like this:

```
session.query(Employee).all()

SELECT
    pjoin.id AS pjoin_id,
    pjoin.name AS pjoin_name,
    pjoin.type AS pjoin_type,
    pjoin.manager_data AS pjoin_manager_data,
    pjoin.engineer_info AS pjoin_engineer_info
FROM (
    SELECT
        employee.id AS id,
        employee.name AS name,
        CAST(NULL AS VARCHAR(50)) AS manager_data,
        CAST(NULL AS VARCHAR(50)) AS engineer_info,
        'employee' AS type
    FROM employee
    UNION ALL
    SELECT
        manager.id AS id,
        manager.name AS name,
        manager.manager_data AS manager_data,
        CAST(NULL AS VARCHAR(50)) AS engineer_info,
        'manager' AS type
    FROM manager
    UNION ALL
    SELECT
        engineer.id AS id,
        engineer.name AS name,
        CAST(NULL AS VARCHAR(50)) AS manager_data,
        engineer.engineer_info AS engineer_info,
        'engineer' AS type
    FROM engineer
) AS pjoin
```

The above _UNION_ query needs to manufacture `"NULL"` columns for _each subtable_ in order to __accommodate for those columns__ that _aren't members of that particular subclass_.


##### Abstract Concrete Classes

The _concrete mappings_ illustrated thus far show both the _subclasses_ as well as the _base class_ mapped to individual tables. In the _concrete inheritance_ use case, it is __common__ that the __base class is not represented within the database, only the subclasses__. In other words, the _base class_ is `"abstract"`.

Normally, when one would like to _map two different subclasses to individual tables_, and __leave the base class unmapped__, this can be achieved very easily. When using _Declarative_, just declare the base class with the `__abstract__` indicator.

Above, we are __not actually__ making use of SQLAlchemy's inheritance mapping facilities; we can _load and persist_ instances of _AbstractManager_ and _AbstractEngineer_ normally. The situation changes however when we need to _query polymorphically_, that is, we'd like to _emit_ `session.query(AbstractEmployee)` and get back a _collection of AbstractManager and AbstractEngineer instances_. This brings us back into the domain of _concrete inheritance_, and we must __build a special mapper__ against _AbstractEmployee_ in order to achieve this.

To modify our _concrete inheritance_ example to illustrate an `"abstract" base` that is capable of _polymorphic loading_, we will have only an _engineer_ and a _manager_ table and __no employee table__, however the _AbstractEmployee_ mapper will be __mapped directly to the "polymorphic union"__, rather than specifying it locally to the `mapper.with_polymorphic` parameter.

To help with this, _Declarative_ offers a variant of the `ConcreteBase` class called `AbstractConcreteBase` which achieves this __automatically__.

Above, the `registry.configure()` method is invoked, which will __trigger__ the _Employee_ class to be __actually mapped__; _before the configuration step_, the class has __no mapping__ as the _sub-tables_ which it will query from __have not yet been defined__. This process is __more complex__ than that of _ConcreteBase_, in that the __entire mapping of the base class must be delayed until all the subclasses have been declared__. With a mapping like the above, only instances of _Manager_ and _Engineer_ __may be persisted__; _querying against the Employee_ class will __always produce__ _Manager_ and _Engineer_ objects.


##### Classical and Semi-Classical Concrete Polymorphic Configuration

The _Declarative configurations_ illustrated with `ConcreteBase` and `AbstractConcreteBase` are _equivalent to two other forms of configuration_ that __make use of `polymorphic_union()` explicitly__. These configurational forms _make use of_ the `Table` object __explicitly__ so that the `"polymorphic union"` can be __created first, then applied to the mappings__. These are illustrated here to clarify the role of the `polymorphic_union()` function in terms of mapping.

A _semi-classical mapping_ for example makes use of _Declarative_, but __establishes the `Table` objects separately__.

Next, the _UNION_ is produced using `polymorphic_union()`.

```
pjoin = polymorphic_union(
    {
        "employee": employees_table,
        "manager": managers_table,
        "engineer": engineers_table,
    },
    "type",
    "pjoin",
)
```

With the above `Table` objects, the _mappings_ can be produced using `"semi-classical" style`, where we use _Declarative_ in conjunction with the `__table__` argument; our _polymorphic union_ above is passed via `__mapper_args__` to the `mapper.with_polymorphic` parameter.

Alternatively, the same `Table` objects can be used in __fully `"classical"` style__, without using _Declarative_ at all. A constructor similar to that supplied by _Declarative_ is illustrated.

```
pjoin = polymorphic_union(
    {
        "manager": managers_table,
        "engineer": engineers_table,
    },
    "type",
    "pjoin",
)


class Employee(Base):
    __table__ = pjoin
    __mapper_args__ = {
        "polymorphic_on": pjoin.c.type,
        "with_polymorphic": "*",
        "polymorphic_identity": "employee",
    }


class Engineer(Employee):
    __table__ = engineer_table
    __mapper_args__ = {
        "polymorphic_identity": "engineer",
        "concrete": True,
    }


class Manager(Employee):
    __table__ = manager_table
    __mapper_args__ = {
        "polymorphic_identity": "manager",
        "concrete": True,
    }
```

Above, we use `polymorphic_union()` in the same manner as before, except that we __omit the employee table__.


##### Relationships with Concrete Inheritance

In a _concrete inheritance_ scenario, _mapping relationships_ is `challenging` since the __distinct classes do not share a table__. If the relationships only involve specific classes, such as a relationship between _Company_ in our previous examples and _Manager_, special steps aren't needed as these are just two related tables.

However, if _Company_ is to have a `one-to-many relationship` to _Employee_, indicating that the collection may include both _Engineer_ and _Manager_ objects, that implies that _Employee_ __must have polymorphic loading capabilities__ and also that __each table to be related must have a foreign key back to the company table__. An example of such a configuration is as follows.

The next complexity with _concrete inheritance_ and _relationships_ involves when we'd like _one or all_ of `Employee`, `Manager` and `Engineer` to themselves __refer back to `Company`__. For this case, SQLAlchemy has __special behavior__ in that a `relationship()` placed on _Employee_ which __links to__ _Company_ __does not work against the `Manager` and `Engineer` classes__, when _exercised_ at the _instance level_. Instead, a __distinct__ `relationship()` must be applied to each class. In order to achieve __bi-directional behavior__ in terms of _three separate relationships_ which serve as the opposite of `Company.employees`, the `relationship.back_populates` parameter is used between each of the relationships.

The above __limitation__ is related to the current implementation, including that _concrete inheriting classes_ __do not share any of the attributes of the superclass__ and therefore __need distinct relationships__ to be set up.


##### Loading Concrete Inheritance Mappings

The _options_ for _loading with concrete inheritance_ are __limited__; generally, if _polymorphic loading_ is __configured on the mapper__ using one of the _declarative concrete mixins_, it __can't be modified at query time__ in current SQLAlchemy versions. Normally, the `with_polymorphic()` function would be __able to override__ the _style of loading used by concrete_, however due to _current limitations_ this is __not yet supported__.
