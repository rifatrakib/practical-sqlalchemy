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
