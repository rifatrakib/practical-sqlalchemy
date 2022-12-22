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
