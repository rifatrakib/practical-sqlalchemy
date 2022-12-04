## Non-Traditional Mappings


#### Mapping a Class against Multiple Tables

_Mappers_ can be constructed against arbitrary relational units (called _selectables_) in addition to plain tables. For example, the `join()` function _creates a selectable unit comprised of multiple tables_, complete with its own __composite primary key__, which can be mapped in the same way as a `Table`.

```
from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table, join
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property

metadata_obj = MetaData()
Base = declarative_base()

user_table = Table(
    "user",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String),
)

address_table = Table(
    "address",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("email_address", String),
)

user_address_join = join(user_table, address_table)


class AddressUser(Base):
    __table__ = user_address_join
    
    id = column_property(user_table.c.id, address_table.c.id)
    address_id = address_table.c.id
```

In the example above, the _join_ expresses columns for both the _user_ and the _address_ table. The `user.id` and `address.user_id` columns are __equated by foreign key__, so _in the mapping_ they are __defined as one attribute__, `AddressUser.id`, using `column_property()` to __indicate a specialized column mapping__. Based on this part of the _configuration_, the _mapping_ will __copy new primary key values__ *from user.id into the address.user_id* column when a flush occurs.

Additionally, the `address.id` column is __mapped explicitly__ to an attribute named `address_id`. This is to __disambiguate__ the mapping of the `address.id` column from the _same-named_ `AddressUser.id` attribute, which here has been assigned to __refer to the user table combined with the address.user_id foreign key__.

The _natural primary key_ of the above mapping is the _composite_ of (`user.id`, `address.id`), as these are the _primary key_ columns of the _user_ and _address_ table __combined together__. The identity of an `AddressUser` object will be in terms of these two values, and is represented from an `AddressUser` object as (`AddressUser.id`, `AddressUser.address_id`).

When referring to the `AddressUser.id` column, _most SQL expressions_ will make use of __only the first column__ in the list of columns mapped, as the _two columns_ are __synonymous__. However, for the special use case such as a `GROUP BY` expression where __both columns must be referenced__ at the _same time_ while making use of the _proper context_, that is, accommodating for _aliases and similar_, the accessor `Comparator.expressions` may be used:

```
q = session.query(AddressUser).group_by(*AddressUser.id.expressions)
```

> ##### Note
>
> A _mapping against multiple tables_ as illustrated above __supports persistence__, that is, _INSERT, UPDATE and DELETE_ of rows within the targeted tables. However, it __does not support__ an operation that would _UPDATE one table_ and _perform INSERT or DELETE on others_ at the same time for one record. That is, if a record _PtoQ_ is mapped to tables `"p"` and `"q"`, where it has a row based on a _LEFT OUTER JOIN_ of `"p" and "q"`, if an _UPDATE_ proceeds that is to _alter data_ in the `"q"` table in an existing record, the `row in "q"` __must exist__; it __won't emit__ an `INSERT` if the _primary key identity_ is __already present__. If the _row does not exist_, for most DBAPI drivers which support reporting the _number of rows affected_ by an `UPDATE`, the _ORM_ will __fail to detect an updated row and raise an error__; otherwise, the data would be _silently ignored_.
>
> A recipe to allow for an `on-the-fly "insert"` of the related row might make use of the `.MapperEvents.before_update` event and look like:
>
> ```
> from sqlalchemy import event
>
>
>@event.listens_for(PtoQ, "before_update")
>def receive_before_update(mapper, connection, target):
>    if target.some_required_attr_on_q is None:
>        connection.execute(q_table.insert(), {"id": target.id})
>```
>
> where above, a row is `INSERT`ed into the *q_table* table by creating an _INSERT_ construct with `Table.insert()`, then executing it using the given _Connection_ which is the __same one being used to emit other SQL for the flush process__. The _user-supplied logic_ would __have to detect__ that the `LEFT OUTER JOIN` _from "p" to "q"_ __does not have an entry__ for the `"q"` side.


#### Mapping a Class against Arbitrary Subqueries

Similar to _mapping against a join_, a plain `select()` object __can be used with a mapper__ as well. The example fragment below illustrates mapping a class called _Customer_ to a `select()` which __includes a join to a subquery__.

```
from sqlalchemy import Column, ForeignKey, Integer, String, Table, select, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

customers = Table(
    "customers",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
)

orders = Table(
    "orders",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("customer_id", Integer, ForeignKey("customers.id")),
    Column("price", Integer),
)

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

Above, the full row represented by *customer_select* will be _all the columns of the customers table_, in addition to those __columns exposed by the `subq` subquery__, which are *order_count*, *highest_order*, and *customer_id*. Mapping the _Customer_ class to this _selectable_ then __creates a class which will contain those attributes__.

When the _ORM_ __persists__ _new instances_ of `Customer`, __only the customers table will actually receive an INSERT__. This is because the _primary key_ of the _orders_ table is __not represented in the mapping__; the _ORM_ will __only emit an INSERT__ into a table for which it has _mapped the primary key_.

> ##### Note
>
> The practice of _mapping to arbitrary SELECT statements_, especially _complex ones_ as above, is __almost never needed__; it _necessarily_ tends to produce _complex queries_ which are __often less efficient__ than that which would be produced by _direct query construction_. The practice is to some degree based on the very early history of SQLAlchemy where the `mapper()` construct was meant to _represent the primary querying interface_; in modern usage, the _Query_ object can be used to __construct virtually any SELECT statement__, including _complex composites_, and __should be favored__ over the `"map-to-selectable" approach`.


#### Multiple Mappers for One Class

In _modern SQLAlchemy_, a particular class is __mapped by only one so-called primary mapper__ at a time. This _mapper_ is __involved in `three` main areas of functionality__: `querying`, `persistence`, and `instrumentation` of the mapped class. The _rationale_ of the _primary mapper_ relates to the fact that the `mapper()` __modifies the class itself__, not only __persisting__ it towards a particular `Table`, but also __instrumenting attributes__ upon the class which are _structured specifically according to the table metadata_. It's __not possible__ for _more than one mapper to be associated with a class in equal measure_, since __only one mapper can actually instrument the class__.

The concept of a `"non-primary" mapper` had existed for many versions of SQLAlchemy however as of version 1.3 this feature is __deprecated__. The one case where such a _non-primary mapper_ is useful is when _constructing a relationship to a class against an alternative selectable_. This use case is now suited using the `aliased` construct and is described at `Relationship to Aliased Class`.

As far as the use case of a class that can actually be _fully persisted to different tables under different scenarios_, very early versions of SQLAlchemy offered a feature for this adapted from _Hibernate_, known as the `"entity name" feature`. However, this use case __became infeasible__ within SQLAlchemy once the _mapped class itself became the source of SQL expression construction_; that is, the __class' attributes themselves link directly to mapped table columns__. The feature was _removed_ and _replaced_ with a __simple recipe-oriented approach__ to accomplishing this task without any ambiguity of _instrumentation_ - to __create new subclasses, each mapped individually__. This pattern is now available as a recipe at `Entity Name`.
