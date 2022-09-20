## Working with Database Metadata

With engines and SQL execution down, we are ready to begin some `Alchemy`. The central element of both `SQLAlchemy Core` and `ORM` is the `SQL Expression Language` which allows for fluent, composable construction of SQL queries. The foundation for these queries are _Python objects that represent database concepts like tables and columns_. These objects are known collectively as __database metadata__.

The most common foundational objects for database metadata in SQLAlchemy are known as `MetaData, Table, and Column`. The sections below will illustrate how these objects are used in both a Core-oriented style as well as an ORM-oriented style.


#### Setting up MetaData with Table objects

When we work with a relational database, the basic structure that we create and query from is known as a `table`. In SQLAlchemy, the `table` is represented by a Python class similarly named `Table`.

To start using the `SQLAlchemy Expression Language`, we will want to have `Table` objects constructed that represent all of the database tables we are interested in working with. Each `Table` may be __declared__, meaning we _explicitly spell out in source code what the table looks like_, or may be __reflected__, which means we _generate the object based on what’s already present in a particular database_. The two approaches can also be blended in many ways.

Whether we will _declare_ or _reflect_ our tables, we start out with a collection that will be where we place our tables known as the `MetaData` object. This object is essentially a `facade around a Python dictionary` that stores a series of `Table` objects keyed to their string name.

Having `a single MetaData object` for an entire application is the most common case, represented as a _module-level variable_ in a single place in an application, often in a __models__ or __dbschema__ type of package. There can be `multiple MetaData collections` as well, however it's typically _most helpful if a series of Table objects that are related to each other belong to a single MetaData collection_.

_Once we have a `MetaData` object, we can declare some `Table` objects_. This tutorial will start with the classic SQLAlchemy tutorial model, that of the table `user`, which would for example _represent the users of a website_, and the table `address`, representing a list of _email addresses associated with rows in the user table_. We normally assign each `Table` object to a variable that will be how we will refer to the table in application code.

A`Table` construct looks a lot like a `SQL CREATE TABLE statement`; starting with the _table name, then listing out each column, where each column has a name and a datatype_. The objects we use above are:

* __`Table`__ - represents a database table and assigns itself to a `MetaData` collection.

* __`Column`__ - represents a column in a database table, and assigns itself to a `Table` object. The `Column` usually includes _a string name and a type object_. The collection of Column objects in terms of the parent `Table` are typically accessed via an associative array located at `Table.c`.


#### Declaring Simple Constraints

The first Column in the above `user_table` includes the `Column.primary_key` parameter which is a shorthand technique of indicating that this `Column` should be part of the _primary key_ for this table. The _primary key_ itself is normally declared implicitly and is represented by the `PrimaryKeyConstraint` construct, which we can see on the `Table.primary_key` attribute on the `Table` object.

The constraint that is most typically declared explicitly is the `ForeignKeyConstraint` object that corresponds to a database _foreign key constraint_. When we declare tables that are related to each other, SQLAlchemy uses the presence of these _foreign key constraint_ declarations not only so that they are emitted within `CREATE statements` to the database, but also to assist in `constructing SQL expressions`.

A `ForeignKeyConstraint` that involves only a single column on the target table is typically declared using a _column-level shorthand notation_ via the `ForeignKey` object. When using the `ForeignKey` object within a `Column` definition, _we can omit the datatype for that `Column`_; it is __automatically inferred__ from that of the related column.

To make a field required, use a third kind of _constraint_, which in SQL is the _`NOT NULL` constraint_, indicated using the `Column.nullable` parameter.


#### Emitting DDL to the Database

After having constructed a fairly elaborate object hierarchy to represent a few database tables, starting at the root `MetaData` object, then into those `Table` objects, each of which hold onto _a collection of `Column` and `Constraint` objects_. This object structure will be at the center of most operations we perform with both _Core_ and _ORM_ going forward.

The first useful thing we can do with this structure will be to emit `CREATE TABLE statements`, or `DDL`, to our target database so that we can _insert_ and _query_ data from them. We have already all the tools needed to do so, by invoking the `MetaData.create_all()` method on our `MetaData`, sending it the `Engine` that refers to the target database.

The `DDL` create process by default includes some `SQLite-specific PRAGMA statements` that _test for the existence of each table before emitting a CREATE_. The full series of steps are also included _within a BEGIN/COMMIT pair_ to accommodate for `transactional DDL` _(`SQLite` does actually support `transactional DDL`, however the `sqlite3` database driver historically runs DDL in `autocommit mode`)_.

The create process also takes care of emitting `CREATE statements` in the correct order. In more complicated dependency scenarios the `FOREIGN KEY constraints` may also be applied to tables after the fact using `ALTER`.

The `MetaData` object also features a `MetaData.drop_all()` method that will emit `DROP statements` in the __reverse order__ as it would emit `CREATE` in order to _drop schema elements_.

##### Migration tools are usually appropriate

Overall, the `CREATE/DROP` feature of `MetaData` is useful for test suites, small and/or new applications, and applications that use short-lived databases. For management of an application database schema over the long term however, a _schema management tool_ such as [`Alembic`](https://alembic.sqlalchemy.org/en/latest/), which builds upon `SQLAlchemy`, is likely a better choice, as it can __manage and orchestrate__ the process of incrementally _altering a fixed database schema over time_ as the design of the application changes.


#### Defining Table Metadata with the ORM

When using the ORM, the process by which we declare `Table` metadata is usually combined with the process of _declaring mapped classes_. The mapped class is any `Python class` we'd like to create, which will then have _attributes on it that will be linked to the columns in a database table_. While there are _a few varieties_ of how this is achieved, the most common style is known as __declarative__, and allows us to declare our _user-defined classes_ and `Table` metadata at once.

##### Setting up the Registry

When using the `ORM`, the `MetaData` collection remains present, however it itself is contained within an `ORM-only object` known as the `registry`. We create a `registry` by constructing it. The `registry`, when constructed, _automatically_ includes a `MetaData` object that will store a collection of `Table` objects.

Instead of declaring `Table` objects directly, we will now declare them indirectly through directives applied to our mapped classes. In the most common approach, each mapped class _descends from a common base class_ known as the `declarative base`. We get a new declarative base from the `registry` using the `registry.generate_base()` method.

The steps of creating the `registry` and `declarative base` classes can be _combined_ into one step using the _historically_ familiar `declarative_base()` function:

```
from sqlalchemy.orm import declarative_base
Base = declarative_base()
```

##### Declaring Mapped Classes

The `Base` object above is a Python class which will serve as the _base class for the ORM mapped classes_ we declare. We can now define _ORM mapped classes_ for the `user` and `address` table in terms of new classes `User` and `Address`.

```
class User(Base):
    __tablename__ = "user_account"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String)
    
    addresses = relationship("Address", back_populates="user")
    
    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Address(Base):
    __tablename__ = "address"
    
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user_account.id"))
    
    user = relationship("User", back_populates="addresses")
    
    def __repr__(self):
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"
```

The above two classes are now our mapped classes, and are available for use in `ORM persistence and query operations`, which will be described later. But they also include `Table` objects that were generated as part of the _declarative mapping process_, and are equivalent to the ones that we declared directly in the previous Core section. We can see these `Table` objects from a declarative mapped class using the `.__table__` attribute.

This `Table` object is generated from the _declarative process_ based on the `.__tablename__` attribute defined on each of our classes, as well as through the use of `Column` objects assigned to _class-level attributes_ within the classes. These `Column` objects can usually be declared _without an explicit `name` field_ inside the constructor, as the _Declarative process_ will name them __automatically based on the attribute name__ that was used.

##### Other Mapped Class Details

For a few quick explanations for the classes above, note the following attributes:

* __the classes have an automatically generated `__init__()` method__ - both classes by default receive an `__init__()` method that allows for parameterized construction of the objects. We are free to provide our own `__init__()` method as well. The `__init__()` allows us to create instances of __User__ and __Address__ passing attribute names, most of which above are linked directly to `Column` objects, as parameter names:

```
sandy = User(name="sandy", fullname="sandy cheeks")
```

* __provided a `__repr__()` method__ - this is fully _optional_, and is strictly so that our custom classes have a _descriptive string representation_ and is not otherwise required:

```
>>> sandy
User(id=None, name='sandy', fullname='Sandy Cheeks')
```

An interesting thing to note above is that the _id attribute automatically returns None_ when accessed, rather than raising `AttributeError` as would be the usual Python behavior for missing attributes.

* __included a `bidirectional` relationship__ - this is another _fully optional construct_, where we made use of an ORM construct called `relationship()` on both classes, which indicates to the ORM that these `User` and `Address` classes refer to each other in a `one to many/many to one relationship`.


##### Emitting DDL to the database

This section is named the same as the section `Emitting DDL` to the Database discussed in terms of Core. This is because `emitting DDL` with our ORM mapped classes is not any different. If we wanted to `emit DDL` for the `Table` objects we've created as part of our declaratively mapped classes, we still can use `MetaData.create_all()` as before.

In our case, we have already generated the `user` and `address` tables in our _SQLite database_. If we had not done so already, we would be free to make use of the `MetaData` associated with our `registry` and _ORM declarative base class_ in order to do so, using `MetaData.create_all()`.


##### Combining Core Table Declarations with ORM Declarative

As an alternative approach to the mapping process shown previously at _Declaring Mapped Classes_, we may also make use of the `Table` objects we created directly in the section `Setting up MetaData with Table objects` in conjunction with declarative mapped classes from a `declarative_base()` generated base class.

This form is called `hybrid table`, and it consists of assigning to the `.__table__` attribute directly, rather than having the declarative process generate it.

> The above example is an alternative form to the mapping that's first illustrated previously at _Declaring Mapped Classes_. This example is for illustrative purposes only, and is not part of this tutorial's `"doctest"` steps, and as such does not need to be run for readers who are executing code examples. The mapping here and the one at _Declaring Mapped Classes_ produce equivalent mappings, but in general one would use only one of these two forms for particular mapped class.

The above two classes are equivalent to those which we declared in the previous mapping example.

The traditional `"declarative base"` approach using `__tablename__` to automatically generate `Table` objects remains the most popular method to declare table metadata. However, disregarding the ORM mapping functionality it achieves, as far as table declaration it's merely a __syntactical convenience__ on top of the `Table` constructor.

We will next refer to our ORM mapped classes above when we talk about _data manipulation_ in terms of the ORM, in the section `Inserting Rows with the ORM`.


#### Table Reflection

To round out the section on working with table `metadata`, we will illustrate another operation that was mentioned at the beginning of the section, that of `table reflection`. `Table reflection` refers to the _process of generating `Table` and related objects by reading the current state of a database_. Whereas in the previous sections we’ve been declaring `Table` objects in Python and then `emitting DDL` to the database, the reflection process does it in _reverse_.

As an example of reflection, we will _create a new `Table` object_ which represents the `table_name` object we created manually in the earlier sections of this document. There are again _some varieties_ of how this is performed, however the __most basic__ is to _construct a `Table` object_, given the _name of the table and a MetaData collection_ to which it will belong, then instead of indicating individual `Column` and `Constraint` objects, _pass it the target `Engine`_ using the `Table.autoload_with` parameter.

At the end of the process, the `some_table` object now _contains the information about the `Column` objects present in the table_, and the object is _usable in exactly the same way_ as a `Table` that we declared explicitly.
