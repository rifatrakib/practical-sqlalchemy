## Table Configuration with Declarative

As introduced at `Declarative Mapping`, the _Declarative style_ includes the ability to _generate_ a __mapped `Table` object__ at the _same time_, or to _accommodate_ a __`Table` or other `FromClause` object directly__.

The following examples assume a `declarative base class` as:

```
from sqlalchemy.orm import declarative_base

Base = declarative_base()
```

All of the examples that follow _illustrate_ a __class inheriting from the above `Base`__. The _decorator style_ introduced at `Declarative Mapping using a Decorator (no declarative base)` is __fully supported__ with all the following examples as well.


#### Declarative Table

With the `declarative base class`, the _typical form of mapping_ includes an attribute `__tablename__` that indicates the name of a `Table` that should be __generated along with the mapping__.

Above, `Column` objects are __placed inline__ with the class definition. The `declarative mapping process` will _generate_ a new_ `Table` _object_ against the __`MetaData` collection associated with the `declarative base`__, and each specified `Column` object will become part of the __`Table.columns` collection__ of this `Table` object. The `Column` objects can omit their `"name"` field, which is usually the _first positional argument_ to the `Column` constructor; the `declarative system` will assign the __key associated with each `Column`__ as the `name`.


#### Accessing Table and Metadata

A `declaratively mapped class` will __always include__ an attribute called `__table__`; when the above _configuration_ using `__tablename__` is __complete__, the _declarative process_ makes the `Table` available via the `__table__` attribute.

The above table is __ultimately the same__ one that _corresponds_ to the `Mapper.local_table` attribute, which we can see through the `runtime inspection system`.

The `MetaData` collection _associated_ with both the `declarative registry` as well as the `base class` is __frequently necessary__ in order to _run DDL operations_ such as `CREATE`, as well as in _use with migration tools_ such as [`Alembic`](https://alembic.sqlalchemy.org/en/latest/index.html). This object is available via the `.metadata` attribute of `registry` as well as the `declarative base class`.


#### Declarative Table Configuration

When using `Declarative Table configuration` with the `__tablename__` declarative class attribute, _additional arguments_ to be supplied to the `Table` constructor should be provided using the `__table_args__` declarative class attribute.

This attribute __accommodates both positional as well as keyword arguments__ that are normally sent to the `Table` constructor. The attribute _can be specified_ in __one of two forms__. One is as a `dictionary`. The other, a `tuple`, where _each argument_ is `positional` (__usually constraints__). _Keyword arguments_ can be specified with the above form by specifying the __last argument__ as a `dictionary`.

A class _may also specify_ the `__table_args__` declarative attribute, as well as the `__tablename__` attribute, in a __dynamic style__ using the `declared_attr()` method _decorator_. See the section `Mixin and Custom Base Classes` for examples on how this is often used.


#### Explicit Schema Name with Declarative Table

The _schema name_ for a `Table` as documented at `Specifying the Schema Name` is __applied to an individual `Table`__ using the `Table.schema` argument. When using `Declarative tables`, this option is __passed like any other__ to the `__table_args__` dictionary.

The _schema name_ can also be __applied to all `Table` objects globally__ by using the `MetaData.schema` parameter documented at `Specifying a Default Schema Name with MetaData`. The `MetaData` object may be __constructed separately__ and _passed_ either to `registry()` or `declarative_base()`.


##### Appending additional columns to an existing Declarative mapped class

A _declarative table configuration_ __allows the addition__ of _new_ `Column` objects to an _existing mapping_ __after__ the `Table` metadata has _already been generated_.

For a `declarative class` that is _declared_ using a `declarative base class`, the _underlying metaclass_ `DeclarativeMeta` includes a `__setattr__()` method that will __intercept additional `Column` objects__ and __add them to both__ the `Table` using `Table.append_column()` as well as to the __existing Mapper__ using `Mapper.add_property()`.

_Additional_ `Column` _objects_ may also be __added to a mapping__ in the specific circumstance of using __`single table inheritance`__, where _additional columns_ are __present on mapped subclasses__ that have __no `Table` of their own__. This is illustrated in the section `Single Table Inheritance`.


#### Declarative with Imperative Table (a.k.a. Hybrid Declarative)

`Declarative mappings` may also be provided with a _pre-existing_ `Table` object, or otherwise a `Table` or other arbitrary `FromClause` construct (such as a `Join` or `Subquery`) that is __constructed separately__.

This is referred to as a __`"hybrid declarative" mapping`__, as the class is mapped using the _declarative style_ for everything involving the `mapper configuration`, however the _mapped_ `Table` _object_ is __produced separately__ and _passed_ to the `declarative process` __directly__.

Above, a `Table` object is constructed using the approach described at `Describing Databases with MetaData`. It __can then be applied directly__ to a class that is `declaratively mapped`. The `__tablename__` and `__table_args__` _declarative class attributes_ are __not used__ in this form. The above _configuration_ is __often more readable__ as an _inline definition_.

A _natural effect_ of the above style is that the `__table__` attribute is itself __defined within the `class definition block`__. As such it __may be immediately referred__ towards _within subsequent attributes_, such as the example below which illustrates _referring to the type column_ in a __polymorphic__ `mapper configuration`.

The __`"imperative table"`__ form is also used when a __non-`Table` construct__, such as a `Join` or `Subquery` object, is _to be mapped_.

```
subq = (
    select(
        func.count(orders.c.id).label("order_count"),
        func.max(orders.c.price).label("highest_order"),
        orders.c.customer_id,
    ).group_by(orders.c.customer_id).subquery()
)

customer_select = (
    select(customers, subq).
    join_from(customers, subq, customers.c.id == subq.c.customer_id).
    subquery()
)


class Customer(Base):
    __table__ = customer_select
```

For _background_ on `mapping to non-Table constructs` see the sections `Mapping a Class against Multiple Tables` and `Mapping a Class against Arbitrary Subqueries`.

The `"imperative table"` form is of particular use __when the class itself is using an alternative form of attribute declaration__, such as `Python dataclasses`. See the section `Applying ORM Mappings to an existing dataclass` for detail.


#### Mapping Declaratively with Reflected Tables

There are _several patterns available_ which provide for producing _mapped classes_ against a _series_ of `Table` objects that were __introspected from the database__, using the _reflection process_ described at `Reflecting Database Objects`.

A _very simple way_ to __map a class to a table reflected from the database__ is to use a `declarative hybrid mapping`, passing the `Table.autoload_with` parameter to the `Table`.

A __major downside__ to the above approach is that the _mapped classes cannot be declared until the tables have been reflected_, which __requires__ the `database connectivity source` __to be present__ while the `application classes` are _being declared_; it's _typical_ that _classes are declared as the modules of an application are being imported_, but `database connectivity` __isn't available until the application starts__ running code so that it can _consume configuration information_ and __create an engine__. There are _currently_ `two approaches` to __working around__ this.


##### Using DeferredReflection

To _accommodate_ the use case of _declaring mapped classes_ where `reflection of table metadata` can __occur afterwards__, a _simple extension_ called the `DeferredReflection mixin` is available, which __alters__ the _declarative mapping process_ to be __delayed until__ a special class-level `DeferredReflection.prepare()` method is called, which will __perform the reflection process__ against a `target database`, and will _integrate the results_ with the `declarative table mapping process`, that is, classes which use the `__tablename__` attribute.

Above, we create a _mixin class_ `Reflected` that will __serve as a base__ for classes in our _declarative hierarchy_ that should become mapped when the `Reflected.prepare` method is called. The above mapping is __not complete until we do so__, given an `Engine`.

The _purpose_ of the `Reflected` class is to __define the scope at which classes should be reflectively mapped__. The plugin will _search_ among the `subclass tree` of the target against which `.prepare()` is called and __reflect all tables which are named by declared classes__; tables in the _target database_ that are _not part of mappings_ and are _not related to the target tables via foreign key constraint_ __will not be reflected__.


##### Using Automap

A more _automated solution_ to __mapping against an existing database__ where _table reflection_ is to be used is to use the `Automap` extension. This extension will __generate entire mapped classes from a database schema__, __including relationships between classes__ based on _observed_ `foreign key` _constraints_. While it _includes hooks for customization_, such as hooks that allow __custom class naming__ and __relationship naming__ schemes, `automap` is oriented towards an expedient __zero-configuration style of working__. If an application wishes to have a _fully explicit model_ that makes use of _table reflection_, the `Using DeferredReflection` may be _preferable_.
