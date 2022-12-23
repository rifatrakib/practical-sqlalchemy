## Configuring how Relationship Joins

`relationship()` will _normally_ create a _join between two tables_ by _examining the foreign key relationship_ between the two tables to __determine which columns should be compared__. There are a variety of situations where this behavior needs to be customized.


#### Handling Multiple Join Paths

One of the most common situations to deal with is when there are _more than one foreign key path between two tables_. Consider a _Customer_ class that __contains two foreign keys__ to an `Address` class.

```
class Customer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    billing_address_id = Column(Integer, ForeignKey("address.id"))
    shipping_address_id = Column(Integer, ForeignKey("address.id"))

    billing_address = relationship("Address")
    shipping_address = relationship("Address")


class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True)
    street = Column(String)
    city = Column(String)
    state = Column(String)
    zip = Column(String)
```

The above mapping, when we attempt to use it, will produce the error:

```
sqlalchemy.exc.AmbiguousForeignKeysError: Could not determine join
condition between parent/child tables on relationship
Customer.billing_address - there are multiple foreign key
paths linking the tables.  Specify the 'foreign_keys' argument,
providing a list of those columns which should be
counted as containing a foreign key reference to the parent table.
```

The above message is pretty long. There are _many potential messages_ that `relationship()` can return, which have been __carefully tailored to detect a variety of common configurational issues__; most will __suggest__ the _additional configuration_ that's needed to __resolve__ the _ambiguity or other missing information_.

In this case, the message wants us to __qualify__ each `relationship()` by _instructing for each one which foreign key column should be considered_, and the appropriate form is as follows.

```
class Customer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    billing_address_id = Column(Integer, ForeignKey("address.id"))
    shipping_address_id = Column(Integer, ForeignKey("address.id"))

    billing_address = relationship("Address", foreign_keys=[billing_address_id])
    shipping_address = relationship("Address", foreign_keys=[shipping_address_id])
```

Above, we specify the *foreign_keys* argument, which is a _Column_ or _list of Column_ objects which __indicate those columns to be considered "foreign"__, or in other words, the columns that contain a value referring to a parent table. Loading the `Customer.billing_address` relationship from a _Customer_ object will use the value present in *billing_address_id* in order to __identify the row in `Address` to be loaded__; similarly, *shipping_address_id* is used for the *shipping_address* relationship. The linkage of the two columns also plays a role during _persistence_; the _newly generated primary key_ of a __just-inserted__ `Address` object will be __copied into the appropriate foreign key column__ of an _associated Customer object_ during a flush.

When specifying *foreign_keys* with Declarative, we can also use _string names_ to specify, however it is __important that if using a list, the list is part of the string__:

```
billing_address = relationship("Address", foreign_keys="[Customer.billing_address_id]")
```

In this specific example, the list is __not necessary__ in any case as there's _only one Column_ we need:

```
billing_address = relationship("Address", foreign_keys="Customer.billing_address_id")
```

> ##### Warning
>
> When passed as a _Python-evaluable string_, the `relationship.foreign_keys` argument is interpreted using Python's `eval()` function. __DO NOT PASS UNTRUSTED INPUT TO THIS STRING__.


#### Specifying Alternate Join Conditions

The _default behavior_ of `relationship()` when constructing a join is that it __equates the value of primary key columns on one side to that of foreign-key-referring columns on the other__. We __can change__ this criterion to be anything we'd like using the `relationship.primaryjoin` argument, as well as the `relationship.secondaryjoin` argument in the case when a _"secondary" table_ is used.

In the example below, using the _User_ class as well as an _Address_ class which stores a street address, we create a relationship *boston_addresses* which will only load those Address objects which specify a city of "Boston".

```
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    boston_addresses = relationship(
        "Address",
        primaryjoin="and_(User.id==Address.user_id, Address.city=='Boston')",
    )


class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    street = Column(String)
    city = Column(String)
    state = Column(String)
    zip = Column(String)
```

Within this string SQL expression, we made use of the `and_()` conjunction construct to __establish two distinct predicates__ for the _join condition_ - joining both the _User.id_ and *Address.user_id* columns to each other, as well as __limiting rows__ in _Address_ to just `city='Boston'`. When using Declarative, rudimentary SQL functions like `and_()` are __automatically available__ in the evaluated namespace of a __string `relationship()` argument__.

> ##### Warning
>
> When passed as a _Python-evaluable string_, the `relationship.foreign_keys` argument is interpreted using Python's `eval()` function. __DO NOT PASS UNTRUSTED INPUT TO THIS STRING__.

The custom criteria we use in a `relationship.primaryjoin` is generally __only significant__ when SQLAlchemy is _rendering SQL in order to load or represent this relationship_. That is, it's used in the SQL statement that's emitted in order to _perform a per-attribute lazy load_, or when a join is _constructed at query time_, such as via `Query.join()`, or via the __`eager "joined"` or `"subquery"` styles of loading__. When _in-memory objects_ are being _manipulated_, we can place any _Address_ object we'd like into the *boston_addresses* collection, regardless of what the value of the `.city` attribute is. The objects will remain __present in the collection until the attribute is expired and re-loaded__ from the database where the criterion is applied. When a _flush_ occurs, the objects inside of *boston_addresses* will be __flushed unconditionally__, assigning value of the primary key _user.id_ column onto the __foreign-key-holding__ *address.user_id* column for each row. The city criteria has __no effect__ here, as the _flush process_ only cares about __synchronizing primary key values into referencing foreign key values__.


#### Creating Custom Foreign Conditions

Another element of the _primary join condition_ is how those columns considered __`"foreign"`__ are determined. Usually, some _subset of Column objects_ will specify _ForeignKey_, or otherwise be _part of a ForeignKeyConstraint_ that's relevant to the join condition. `relationship()` looks to this _foreign key status_ as it decides __how it should load and persist data__ for this relationship. However, the `relationship.primaryjoin` argument can be used to __create a join condition that doesn't involve any `"schema"` level foreign keys__. We can combine `relationship.primaryjoin` along with *relationship.foreign_keys* and *relationship.remote_side* __explicitly__ in order to establish such a join.

Below, a class _HostEntry_ joins to itself, equating the string content column to the ip_address column, which is a _PostgreSQL_ type called _INET_. We need to use `cast()` in order to cast one side of the join to the type of the other.

```
class HostEntry(Base):
    __tablename__ = "host_entry"
    
    id = Column(Integer, primary_key=True)
    ip_address = Column(INET)
    content = Column(String(50))
    
    # relationship() using explicit foreign_keys, remote_side
    parent_host = relationship(
        "HostEntry",
        primaryjoin=ip_address == cast(content, INET),
        foreign_keys=content,
        remote_side=ip_address,
    )
```

The above relationship will produce a join like:

```
SELECT host_entry.id, host_entry.ip_address, host_entry.content
FROM host_entry JOIN host_entry AS host_entry_1
ON host_entry_1.ip_address = CAST(host_entry.content AS INET)
```

An alternative syntax to the above is to use the `foreign()` and `remote()` _annotations_, __inline within__ the `relationship.primaryjoin` expression. This syntax represents the _annotations_ that `relationship()` __normally applies by itself__ to the join condition given the *relationship.foreign_keys* and *relationship.remote_side* arguments. These functions may be __more succinct when an explicit join condition is present__, and additionally serve to mark exactly the column that is __"foreign"__ or __"remote"__ independent of whether that column is stated multiple times or within complex SQL expressions.


#### Using custom operators in join conditions

Another use case for relationships is the use of custom operators, such as _PostgreSQL_'s __"is contained within"__ `<<` operator when _joining with types such as INET and CIDR_. For _custom boolean operators_ we use the `Operators.bool_op()` function:

```
inet_column.bool_op("<<")(cidr_column)
```

A comparison like the above may be __used directly__ with `relationship.primaryjoin` when _constructing_ a `relationship()`.

```
class IPA(Base):
    __tablename__ = "ip_address"

    id = Column(Integer, primary_key=True)
    v4address = Column(INET)

    network = relationship(
        "Network",
        primaryjoin="IPA.v4address.bool_op('<<')" "(foreign(Network.v4representation))",
        viewonly=True,
    )


class Network(Base):
    __tablename__ = "network"

    id = Column(Integer, primary_key=True)
    v4representation = Column(CIDR)
```

Above, a query such as:

```
session.query(IPA).join(IPA.network)
```

Will render as:

```
SELECT ip_address.id AS ip_address_id, ip_address.v4address AS ip_address_v4address
FROM ip_address JOIN network ON ip_address.v4address << network.v4representation
```


#### Custom operators based on SQL functions

A variant to the use case for `Operators.op.is_comparison` is when we __aren't using an operator, but a SQL function__. The typical example of this use case is the _PostgreSQL PostGIS functions_; however, __any SQL function on any database that resolves to a binary condition may apply__. To suit this use case, the `FunctionElement.as_comparison()` method can __modify any SQL function__, such as those invoked from the _func namespace_, to indicate to the ORM that the function produces a comparison of two expressions. The below example illustrates this with the _Geoalchemy2_ library.

```
class Polygon(Base):
    __tablename__ = "polygon"
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry("POLYGON", srid=4326))
    points = relationship(
        "Point",
        primaryjoin="func.ST_Contains(foreign(Polygon.geom), Point.geom).as_comparison(1, 2)",
        viewonly=True,
    )


class Point(Base):
    __tablename__ = "point"
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry("POINT", srid=4326))
```

Above, the `FunctionElement.as_comparison()` indicates that the `func.ST_Contains()` SQL function is __comparing__ the _Polygon.geom_ and _Point.geom_ expressions. The `foreign()` annotation additionally notes which column takes on the _"foreign key" role_ in this particular relationship.


#### Overlapping Foreign Keys

A rare scenario can arise when _composite foreign keys_ are used, such that a __single column may be the subject of more than one column referred to via foreign key constraint__.

Consider an (admittedly complex) mapping such as the _Magazine_ object, referred to both by the _Writer_ object and the _Article_ object __using a composite primary key scheme__ that includes *magazine_id* for both; then to _make Article refer to Writer as well_, *Article.magazine_id* is involved in __two separate relationships__; _Article.magazine_ and _Article.writer_.

```
class Magazine(Base):
    __tablename__ = "magazine"

    id = Column(Integer, primary_key=True)


class Article(Base):
    __tablename__ = "article"

    article_id = Column(Integer)
    magazine_id = Column(ForeignKey("magazine.id"))
    writer_id = Column()

    magazine = relationship("Magazine")
    writer = relationship("Writer")

    __table_args__ = (
        PrimaryKeyConstraint("article_id", "magazine_id"),
        ForeignKeyConstraint(
            ["writer_id", "magazine_id"], ["writer.id", "writer.magazine_id"]
        ),
    )


class Writer(Base):
    __tablename__ = "writer"

    id = Column(Integer, primary_key=True)
    magazine_id = Column(ForeignKey("magazine.id"), primary_key=True)
    magazine = relationship("Magazine")
```

When the above mapping with _uncommented Article_ is configured, we will see this warning emitted:

```
SAWarning: relationship 'Article.writer' will copy column
writer.magazine_id to column article.magazine_id,
which conflicts with relationship(s): 'Article.magazine'
(copies magazine.id to article.magazine_id). Consider applying
viewonly=True to read-only relationships, or provide a primaryjoin
condition marking writable columns with the foreign() annotation.
```

What this refers to originates from the fact that *Article.magazine_id* is the __subject of two different foreign key constraints__; it refers to _Magazine.id_ directly as a source column, but also refers to *Writer.magazine_id* as a source column in the context of the _composite key to Writer_. If we associate an _Article_ with a particular _Magazine_, but then associate the _Article_ with a _Writer_ that's associated with a __different__ _Magazine_, the ORM will __overwrite__ *Article.magazine_id* __non-deterministically__, silently changing which magazine we refer towards; it may also attempt to place _NULL_ into this column if we _de-associate a Writer from an Article_. The warning lets us know this is the case.

To solve this, we need to __break out the behavior__ of _Article_ to __include all three of the following features__:

1. _Article_ first and foremost writes to *Article.magazine_id* __based on data persisted__ in the _Article.magazine_ relationship only, that is a __value copied__ from _Magazine.id_.

2. _Article_ can write to *Article.writer_id* on behalf of data persisted in the _Article.writer_ relationship, but only the _Writer.id_ column; the *Writer.magazine_id* column __should not be written__ into *Article.magazine_id* as it ultimately is sourced from _Magazine.id_.

3. _Article_ takes *Article.magazine_id* into account when __loading__ _Article.writer_, even though it __doesn't write to it on behalf of this relationship__.

To get just `#1` and `#2`, we could specify only *Article.writer_id* as the `"foreign keys"` for _Article.writer_.

```
class Article(Base):
    # ...

    writer = relationship("Writer", foreign_keys="Article.writer_id")
```

However, this has the __effect of `Article.writer` not taking `Article.magazine_id` into account when querying against `Writer`__:

```
SELECT article.article_id AS article_article_id,
    article.magazine_id AS article_magazine_id,
    article.writer_id AS article_writer_id
FROM article
JOIN writer ON writer.id = article.writer_id
```

Therefore, to get at all of `#1`, `#2`, and `#3`, we express the _join condition_ as well as which __columns to be written by combining `relationship.primaryjoin` fully__, along with either the `relationship.foreign_keys` argument, or __more succinctly__ by _annotating_ with `foreign()`.

```
class Article(Base):
    # ...

    writer = relationship(
        "Writer",
        primaryjoin="and_(Writer.id == foreign(Article.writer_id), "
        "Writer.magazine_id == Article.magazine_id)",
    )
```
