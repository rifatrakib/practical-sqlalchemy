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


#### Non-relational Comparisons / Materialized Path

Using _custom expressions_ means we can produce __unorthodox join conditions__ that _don't obey the usual primary/foreign key model_. One such example is the `materialized path pattern`, where we __compare strings for overlapping path tokens in order to produce a tree structure__.

Through careful use of `foreign()` and `remote()`, we can build a _relationship_ that effectively produces a __rudimentary materialized path system__. Essentially, when `foreign()` and `remote()` are on the __same side__ of the comparison expression, the _relationship_ is considered to be _"one to many"_; when they are on __different sides__, the _relationship_ is considered to be _"many to one"_. For the comparison we'll use here, we'll be dealing with collections so we keep things configured as _"one to many"_.

```
class Element(Base):
    __tablename__ = "element"

    path = Column(String, primary_key=True)

    descendants = relationship(
        "Element",
        primaryjoin=remote(foreign(path)).like(path.concat("/%")),
        viewonly=True,
        order_by=path,
    )
```

Above, if given an _Element_ object with a path attribute of _"/foo/bar2"_, we seek for a load of _Element.descendants_ to look like:

```
SELECT element.path AS element_path
FROM element
WHERE element.path LIKE ('/foo/bar2' || '/%') ORDER BY element.path
```


#### Self-Referential Many-to-Many Relationship

_Many to many relationships_ can be customized by _one or both_ of `relationship.primaryjoin` and `relationship.secondaryjoin` - the _latter_ is __significant__ for a relationship that specifies a _many-to-many reference_ using the `relationship.secondary` argument. A common situation which involves the usage of `relationship.primaryjoin` and `relationship.secondaryjoin` is when __establishing a many-to-many relationship from a class to itself__.

```
node_to_node = Table(
    "node_to_node",
    Base.metadata,
    Column("left_node_id", Integer, ForeignKey("node.id"), primary_key=True),
    Column("right_node_id", Integer, ForeignKey("node.id"), primary_key=True),
)


class NodeObject(Base):
    __tablename__ = "node_object"
    id = Column(Integer, primary_key=True)
    label = Column(String)
    right_nodes = relationship(
        "NodeObject",
        secondary=node_to_node,
        primaryjoin=id == node_to_node.c.left_node_id,
        secondaryjoin=id == node_to_node.c.right_node_id,
        backref="left_nodes",
    )
```

Where above, SQLAlchemy __can't know automatically__ which columns should connect to which for the *right_nodes* and *left_nodes* relationships. The `relationship.primaryjoin` and `relationship.secondaryjoin` arguments _establish how we'd like to join to the association table_. In the Declarative form above, as we are declaring these conditions within the Python block that corresponds to the _NodeObject_ class, the _id_ variable is __available directly as the Column object__ we wish to join with.

Alternatively, we can define the `relationship.primaryjoin` and `relationship.secondaryjoin` arguments using strings, which is __suitable__ in the case that our __configuration does not have__ either the _NodeObject.id_ column object available yet or the *node_to_node* table perhaps __isn't yet available__. When referring to a plain _Table_ object in a declarative string, we use the string name of the table as it is present in the _MetaData_.

```
class NodeString(Base):
    __tablename__ = "node_string"
    id = Column(Integer, primary_key=True)
    label = Column(String)
    right_nodes = relationship(
        "NodeString",
        secondary="node_to_node",
        primaryjoin="NodeString.id==node_to_node.c.left_node_id",
        secondaryjoin="NodeString.id==node_to_node.c.right_node_id",
        backref="left_nodes",
    )
```

> ##### Warning
>
> When passed as a _Python-evaluable string_, the `relationship.foreign_keys` argument is interpreted using Python's `eval()` function. __DO NOT PASS UNTRUSTED INPUT TO THIS STRING__.

A _classical mapping situation_ here is similar, where *node_to_node_meta* __can be joined__ to *node_var.c.id*.

```
node_to_node_meta = Table(
    "node_to_node_meta",
    metadata_obj,
    Column("left_node_id", Integer, ForeignKey("node.id"), primary_key=True),
    Column("right_node_id", Integer, ForeignKey("node.id"), primary_key=True),
)

node_var = Table(
    "node_var",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("label", String),
)


class NodeVar(object):
    pass


mapper_registry.map_imperatively(
    NodeVar,
    node_var,
    properties={
        "right_nodes": relationship(
            NodeVar,
            secondary=node_to_node_meta,
            primaryjoin=node_var.c.id == node_to_node_meta.c.left_node_id,
            secondaryjoin=node_var.c.id == node_to_node_meta.c.right_node_id,
            backref="left_nodes",
        )
    },
)
```

Note that in both examples, the `relationship.backref` keyword specifies a *left_nodes* backref - when `relationship()` __creates the second relationship in the reverse direction__, it's __smart enough__ to __reverse__ the _relationship.primaryjoin_ and _relationship.secondaryjoin_ arguments.


#### Composite `"Secondary"` Joins

Sometimes, when one seeks to build a `relationship()` between two tables there is a __need for more than just two or three tables__ to be involved in order to join them. This is an area of `relationship()` where one seeks to _push the boundaries_ of what's possible, and often the ultimate solution to many of these _exotic use cases_ needs to be _hammered out_ on the SQLAlchemy mailing list.

In more recent versions of SQLAlchemy, the `relationship.secondary` parameter can be used in some of these cases in order to provide a __composite target consisting of multiple tables__.

In the above example, we provide all three of _relationship.secondary_, _relationship.primaryjoin_, and _relationship.secondaryjoin_, in the declarative style _referring to the named tables a, b, c, d_ __directly__. A query from A to D looks like:

```
session.query(A).join(A.d).all()

SELECT a.id AS a_id, a.b_id AS a_b_id
FROM a JOIN (
    b AS b_1 JOIN d AS d_1 ON b_1.d_id = d_1.id
        JOIN c AS c_1 ON c_1.d_id = d_1.id)
    ON a.b_id = b_1.id AND a.id = c_1.a_id JOIN d ON d.id = b_1.d_id
```

In the above example, we take advantage of being able to __stuff multiple tables into a `"secondary"` container__, so that we can _join across many tables_ while still keeping things _"simple"_ for `relationship()`, in that there's _just "one" table on both the "left" and the "right" side_; the _complexity_ is __kept within the middle__.

> ##### Warning
>
> A relationship like the above is typically marked as `viewonly=True` and should be considered as __read-only__. While there are sometimes ways to make relationships like the above _writable_, this is _generally complicated and error prone_.


#### Relationship to Aliased Class

In the previous section, we illustrated a technique where we used _relationship.secondary_ in order to __place additional tables within a join condition__. There is one _complex join_ case where even this technique is __not sufficient__; when we seek to _join from A to B_, making use of _any number of C, D, etc. in between_, however there are also __join conditions between A and B directly__. In this case, the _join from A to B_ may be __difficult to express with just a complex `relationship.primaryjoin` condition__, as the _intermediary tables may need special handling_, and it is also __not expressible__ with a _relationship.secondary_ object, since the `A->secondary->B` pattern __does not support any references between A and B directly__. When this _extremely advanced case_ arises, we can resort to __creating a second mapping__ as a `target` for the _relationship_. This is where we use `AliasedClass` in order to make a _mapping to a class that includes all the additional tables we need for this join_. In order to produce this mapper as an _"alternative" mapping_ for our class, we use the `aliased()` function to produce the new construct, then use `relationship()` against the object as though it were a plain mapped class.

Below illustrates a `relationship()` with a _simple join from A to B_, however the _primaryjoin_ condition is __augmented with two additional entities__ C and D, which also must have rows that line up with the rows in both A and B simultaneously.

```
class A(Base):
    __tablename__ = "a"
    id = Column(Integer, primary_key=True)
    b_id = Column(ForeignKey("b.id"))


class B(Base):
    __tablename__ = "b"
    id = Column(Integer, primary_key=True)


class C(Base):
    __tablename__ = "c"
    id = Column(Integer, primary_key=True)
    a_id = Column(ForeignKey("a.id"))
    some_c_value = Column(String)


class D(Base):
    __tablename__ = "d"
    id = Column(Integer, primary_key=True)
    c_id = Column(ForeignKey("c.id"))
    b_id = Column(ForeignKey("b.id"))
    some_d_value = Column(String)


# 1. set up the join() as a variable, so we can refer
# to it in the mapping multiple times.
j = join(B, D, D.b_id == B.id).join(C, C.id == D.c_id)

# 2. Create an AliasedClass to B
B_viacd = aliased(B, j, flat=True)

A.b = relationship(B_viacd, primaryjoin=A.b_id == j.c.b_id)
```

With the above mapping, a simple join looks like:

```
session.query(A).join(A.b).all()

SELECT a.id AS a_id, a.b_id AS a_b_id
FROM a JOIN (b JOIN d ON d.b_id = b.id JOIN c ON c.id = d.c_id) ON a.b_id = b.id
```


##### Using the AliasedClass target in Queries

In the previous example, the _A.b_ relationship refers to the *B_viacd* entity as the `target`, and __not the B class directly__. To _add additional criteria_ involving the _A.b_ relationship, it's __typically necessary to reference the B_viacd directly__ rather than using B, especially in a case where the _target entity of A.b_ is to be __transformed__ into an `alias` or a `subquery`. Below illustrates the _same relationship_ using a _subquery_, rather than a join:

```
subq = select(B).join(D, D.b_id == B.id).join(C, C.id == D.c_id).subquery()
B_viacd_subquery = aliased(B, subq)
A.b = relationship(B_viacd_subquery, primaryjoin=A.b_id == subq.c.id)
```

A query using the above _A.b_ relationship will render a `subquery`:

```
session.query(A).join(A.b).all()

SELECT a.id AS a_id, a.b_id AS a_b_id
FROM a JOIN (SELECT b.id AS id, b.some_b_column AS some_b_column
FROM b JOIN d ON d.b_id = b.id JOIN c ON c.id = d.c_id) AS anon_1 ON a.b_id = anon_1.id
```

If we want to _add additional criteria_ based on the _A.b_ join, we must do so in terms of *B_viacd_subquery* rather than B directly:

```
(
    sess.query(A)
    .join(A.b)
    .filter(B_viacd_subquery.some_b_column == "some b")
    .order_by(B_viacd_subquery.id)
).all()

SELECT a.id AS a_id, a.b_id AS a_b_id
FROM a JOIN (SELECT b.id AS id, b.some_b_column AS some_b_column
FROM b JOIN d ON d.b_id = b.id JOIN c ON c.id = d.c_id) AS anon_1 ON a.b_id = anon_1.id
WHERE anon_1.some_b_column = ? ORDER BY anon_1.id
```


#### Row-Limited Relationships with Window Functions

Another interesting use case for relationships to _AliasedClass_ objects are situations where the __relationship needs to join to a specialized `SELECT`__ of any form. One scenario is when the use of a `window function` is desired, such as to __limit how many rows should be returned for a relationship__. The example below illustrates a _non-primary mapper relationship_ that will load the __first ten items for each collection__.

```
class A(Base):
    __tablename__ = "a"
    id = Column(Integer, primary_key=True)


class B(Base):
    __tablename__ = "b"
    id = Column(Integer, primary_key=True)
    a_id = Column(ForeignKey("a.id"))


partition = select(
    B, func.row_number().over(order_by=B.id, partition_by=B.a_id).label("index")
).alias()

partitioned_b = aliased(B, partition)

A.partitioned_bs = relationship(
    partitioned_b, primaryjoin=and_(partitioned_b.a_id == A.id, partition.c.index < 10)
)
```

We can use the above *partitioned_bs* relationship with most of the _loader strategies_, such as `selectinload()`:

```
for a1 in s.query(A).options(selectinload(A.partitioned_bs)):
    print(a1.partitioned_bs)  # <-- will be no more than ten objects
```

Where above, the `"selectinload"` query looks like:

```
SELECT
    a_1.id AS a_1_id, anon_1.id AS anon_1_id, anon_1.a_id AS anon_1_a_id,
    anon_1.data AS anon_1_data, anon_1.index AS anon_1_index
FROM a AS a_1
JOIN (
    SELECT b.id AS id, b.a_id AS a_id, b.data AS data,
    row_number() OVER (PARTITION BY b.a_id ORDER BY b.id) AS index
    FROM b) AS anon_1
ON anon_1.a_id = a_1.id AND anon_1.index < %(index_1)s
WHERE a_1.id IN ( ... primary key collection ...)
ORDER BY a_1.id
```

Above, for _each matching primary key_ in `"a"`, we will get the __first ten "bs" as ordered by "b.id"__. By *partitioning on "a_id"* we ensure that _each "row number"_ is __local to the parent `"a_id"`__.

Such a mapping would _ordinarily_ also __include a "plain" relationship__ from _"A" to "B"_, for _persistence operations_ as well as when the __full set of "B" objects per "A" is desired__.


#### Building Query-Enabled Properties

Very _ambitious custom join conditions_ may __fail to be directly persistable__, and in some cases __may not even load correctly__. To _remove the persistence part_ of the equation, use the flag _relationship.viewonly_ on the `relationship()`, which establishes it as a __read-only attribute__ (_data written to the collection will be ignored on flush()_). However, in _extreme cases_, consider using a _regular Python property in conjunction with Query_.

```
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)

    @property
    def addresses(self):
        return object_session(self).query(Address).with_parent(self).filter(...).all()
```

In other cases, the _descriptor_ can be built to __make use of existing `in-Python` data__.
