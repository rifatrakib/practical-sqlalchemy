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
