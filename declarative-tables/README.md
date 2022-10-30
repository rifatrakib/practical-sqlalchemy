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
