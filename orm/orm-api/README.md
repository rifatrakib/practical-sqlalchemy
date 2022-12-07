## Object Relational Tutorial (1.x API)

The `SQLAlchemy Object Relational Mapper` presents a method of _associating_ __user-defined `Python classes` with `database tables`__, and _instances_ of those classes (_objects_) with `rows` in their corresponding `tables`. It _includes_ a system that __transparently synchronizes all changes in state__ between _objects_ and their _related rows_, called a `unit of work`, as well as a system for _expressing database queries_ in terms of the `user defined classes` and their `defined relationships` between each other.

The `ORM` is in _contrast_ to the `SQLAlchemy Expression Language`, upon which the `ORM` is constructed. Whereas the `SQL Expression Language`, introduced in `SQL Expression Language Tutorial (1.x API)`, presents a system of _representing_ the __primitive constructs of the relational database directly__ _without opinion_, the `ORM` presents a __high level__ and __abstracted__ `pattern of usage`, which itself is an example of applied usage of the _Expression Language_.

While there is __overlap__ among the `usage patterns` of the `ORM` and the `Expression Language`, the __similarities are more superficial__ than they may at first appear. One approaches the _structure and content of data_ from the `perspective` of a __`user-defined domain model`__ which is __transparently persisted and refreshed__ from its _underlying storage model_. The other approaches it from the perspective of __`literal schema` and `SQL expression` representations__ which are __explicitly composed into messages__ _consumed individually by the database_.

A _successful_ `application` may be constructed using the `Object Relational Mapper` __exclusively__. In _advanced situations_, an application constructed with the ORM may make _occasional usage_ of the `Expression Language` __directly__ in certain areas where __specific database interactions are required__.


#### Version Check

A _quick check_ to __verify__ that we are on at `least version 1.4` of `SQLAlchemy`.


#### Connecting

For this notebook we will use an __in-memory-only__ `SQLite database`. To connect we use `create_engine()`.

The `echo` flag is a _shortcut_ to __setting up `SQLAlchemy` logging__, which is accomplished via __Python's standard `logging` module__. With it enabled, we'll see _all the generated SQL produced_. If you are working through this notebook and want _less output generated_, set it to `False`. This notebook will _format_ the `SQL` __behind a popup window__ so it doesn't get in our way; just click the `"SQL"` links to see what's being _generated_.

The _return value_ of `create_engine()` is an __instance of `Engine`__, and it _represents_ the __core interface to the database__, adapted through a `dialect` that _handles the details of the database and DBAPI in use_. In this case the `SQLite dialect` will __interpret instructions__ to the Python _built-in_ `sqlite3` module.

> ##### Lazy Connecting
> The `Engine`, when first returned by `create_engine()`, has __not actually tried to connect__ to the database yet; that _happens only the first time it is asked to perform a task_ against the database.

The first time a method like `Engine.execute()` or `Engine.connect()` is called, the `Engine` _establishes_ a __real `DBAPI` connection__ to the database, which is then __used to emit the SQL__. When using the `ORM`, we typically __don't use the `Engine` directly once created__; instead, it's _used behind the scenes_ by the `ORM` as we'll see shortly.


#### Declare a Mapping

When using the `ORM`, the _configurational process_ __starts by `describing` the database tables__ we'll be dealing with, and then by __defining__ our own `classes` which will be _mapped_ to those `tables`. In _modern SQLAlchemy_, these `two tasks` are _usually_ __performed together__, using a system known as `Declarative Extensions`, which allows us to _create classes_ that __include directives to describe__ the `actual database table` they will be _mapped to_.

Classes _mapped_ using the `Declarative system` are _defined_ in terms of a __base class__ which _maintains_ a __catalog of classes and tables relative to that base__ - this is known as the __`declarative base class`__. Our application will _usually_ have __just one instance of this base__ in a _commonly imported module_. We _create_ the `base class` using the `declarative_base()` function, as follows.

Now that we have a __`"base"`__, we __can define__ _any number of_ `mapped classes` in terms of it. We will start with just a single table called `users`, which will _store records_ for the end-users using our application. A new class called `User` will be the class to which we _map_ this `table`. _Within the class_, we _define_ __details about the table__ to which we'll be __mapping__, _primarily_ the `table name`, and `names` and `datatypes of columns`.

> ##### Tip
> The `User` class defines a `__repr__()` method, but note that is __optional__; we only _implement_ it in this notebook so that our examples show _nicely formatted_ `User` _objects_.

A class using `Declarative` at a _minimum_ __needs a `__tablename__` attribute__, and __at least one `Column`__ which is __part of a `primary key`__. `SQLAlchemy` __never makes any assumptions__ by itself _about the table to which a class refers_, including that it has __no built-in conventions__ for _names, datatypes, or constraints_. But this __doesn't mean boilerplate is required__; instead, you're encouraged to _create_ your __own automated conventions__ using `helper functions` and `mixin classes`, which is described in detail at `Mixin and Custom Base Classes`.

When our class is constructed, `Declarative` __replaces all the `Column` objects__ with _special_ `Python accessors` known as __`descriptors`__; this is a process known as __`instrumentation`__. The `"instrumented"` _mapped class_ will provide us with the means to _refer to our table_ in a `SQL context` as well as to __persist and load the values of columns__ from the database.

__Outside of what the `mapping process` does to our class, the class remains otherwise mostly a `normal Python class`__, to which we can _define any number of ordinary attributes and methods_ needed by our application.


#### Create a Schema

With our `User` class _constructed via_ the __Declarative system__, we have _defined information_ about our `table`, known as __`table metadata`__. The object used by `SQLAlchemy` to _represent this information for a specific table_ is called the `Table object`, and here `Declarative` has made one for us. We can see this object by inspecting the `__table__` _attribute_.

> ##### Classical Mappings
> The `Declarative system`, though _highly recommended_, is __not required__ in order to use _SQLAlchemy's ORM_. _Outside of Declarative_, any _plain Python class_ __can be mapped to any `Table`__ using the `mapper()` function __directly__; this _less common usage_ is described at `Imperative Mapping`.

When we declared our class, `Declarative` used a __Python metaclass__ in order to _perform additional activities_ once the class declaration was __complete__; within this phase, it then _created_ a `Table object` __according to our specifications__, and __associated it with the class__ by constructing a `Mapper object`. This object is a __behind-the-scenes__ object we _normally don't need to deal with directly_ (though it can _provide plenty of information_ about our _mapping_ when we need it).

The `Table` object is a _member_ of a _larger collection_ known as __`MetaData`__. When using `Declarative`, this object is _available_ using the `.metadata` attribute of our _declarative base class_.

The `MetaData` is a __registry__ which includes the ability to _emit a limited set of schema generation commands_ to the database. As our `SQLite` database __does not actually have a users table present__, we can use `MetaData` to _issue_ `CREATE TABLE` statements to the database _for all tables that don't yet exist_. Below, we call the `MetaData.create_all()` method, passing in our `Engine` as a __source of database connectivity__. We will see that _special commands are first emitted_ to _check_ for the __presence of the users table__, and following that the __actual `CREATE TABLE` statement__.

> ##### Minimal Table Descriptions vs. Full Descriptions
> 
> Users familiar with the _syntax_ of `CREATE TABLE` may notice that the _VARCHAR columns were generated_ __without a length__; on `SQLite` and `PostgreSQL`, this is a _valid datatype_, but on _others_, it's _not allowed_. So if running this notebook on one of those databases, and you wish to use `SQLAlchemy` to issue `CREATE TABLE`, a `"length"` may be provided to the `String` type as below:
> 
> `Column(String(50))`
> 
> The _length_ field on `String`, as well as _similar_ `precision/scale` fields available on `Integer`, `Numeric`, etc. are __not referenced__ by `SQLAlchemy` other than when _creating tables_.
> 
> Additionally, `Firebird` and `Oracle` __require `sequences` to generate new primary key identifiers__, and `SQLAlchemy` __doesn't generate or assume__ these _without_ being __instructed__. For that, you use the `Sequence` construct.
> 
> ```
> from sqlalchemy import Sequence
> Column(Integer, Sequence("user_id_seq"), primary_key=True)
> ```
> 
> A _full, foolproof_ `Table` generated via our `declarative mapping` is therefore:
> 
> ```
> class User(Base):
>     __tablename__ = "users"
>     id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
>     name = Column(String(50))
>     fullname = Column(String(50))
>     nickname = Column(String(50))
> 
>     def __repr__(self):
>         return "<User(name='%s', fullname='%s', nickname='%s')>" % (
>             self.name,
>             self.fullname,
>             self.nickname,
>         )
> ```
> 
> We include this _more verbose table definition_ __separately__ to __`highlight`__ the _difference between a minimal construct_ __geared__ _primarily_ towards __in-Python usage only__, versus one that will be _used to emit_ `CREATE TABLE` statements on a _particular set of backends_ with __more stringent requirements__.


#### Create an Instance of the Mapped Class

_With mappings complete_, let's now __create and inspect__ a `User` object.

```
ed_user = User(name="ed", fullname="Ed Jones", nickname="edsnickname")
```

> ##### the `__init__()` method
> Our `User` class, as defined using the `Declarative system`, has been _provided with a constructor_ (e.g. `__init__()` method) which __automatically accepts keyword names that match the columns we've mapped__. We are _free to define_ any __explicit `__init__()` method__ we prefer on our class, which will __override the default method__ provided by `Declarative`.

Even though we __didn't specify__ it in the _constructor_, the `id` attribute __still produces a value of `None`__ when we _access_ it (_as opposed to Python's usual behavior_ of raising `AttributeError` for an _undefined attribute_). `SQLAlchemy`'s __instrumentation__ normally _produces_ this _default value_ for `column-mapped attributes` __when first accessed__. For those attributes where we've _actually assigned a value_, the _instrumentation system_ is __tracking those assignments__ for use _within_ an eventual `INSERT statement` to be __emitted__ to the database.


#### Creating a Session

We're now ready to start talking to the database. The _ORM_'s `"handle"` to the database is the `Session`. When we _first_ __set up the application__, at the _same level_ as our `create_engine()` statement, we define a `Session` class which will __serve as a factory__ for _new_ `Session` objects.

In the case where your _application_ __does not yet have an `Engine`__ when you `define` your _module-level_ objects, just set it up _without bind parameter_. Later, when you _create your engine_ with `create_engine()`, __connect it to the `Session`__ using `sessionmaker.configure()`.

> ##### Session life-cycle patterns
> The question of when to make a `Session` _depends_ a lot on __what kind of application__ is being built. Keep in mind, the `Session` is just a __workspace for your objects__, _local to a particular database connection_ - if you think of an _application thread_ as a guest at a dinner party, the `Session` is the guest's plate and the objects it holds are the food (and the database...the kitchen?)! More on this topic available at `When do I construct a Session, when do I commit it, and when do I close it?`.

This _custom-made_ `Session` class will __create new Session objects__ which are __bound to our database__. Other __`transactional characteristics`__ may be _defined_ when calling `sessionmaker` as well; these are described in a later chapter. Then, whenever you need to _have a conversation with the database_, you __instantiate__ a `Session`.

The above `Session` is __associated__ with our _SQLite-enabled_ `Engine`, but it __hasn't opened any connections__ yet. When it's _first used_, it __retrieves a connection__ from a __pool of connections__ _maintained by_ the `Engine`, and _holds onto it_ until we __`commit` all changes__ _and/or_ __close__ the `session` object.


#### Adding and Updating Objects

To __persist__ our `User` object, we `Session.add()` it to our `Session`. _At this point_, we say that the _instance_ is `pending`; __no SQL has yet been issued__ and the _object_ is __not yet represented by a row in the database__. The `Session` will __issue the SQL to persist__ Ed Jones _as soon as is needed_, using a _process_ known as a `flush`. If we _query the database for Ed Jones_, __all pending information will first be flushed__, and the _query is issued_ __immediately thereafter__.

For example, below we _create a new_ `Query` _object_ which __loads instances of `User`__. We __`"filter by"`__ the _name attribute of ed_, and _indicate_ that we'd like __only the first result__ in the _full list of rows_. A `User` instance is returned which is __equivalent to that which we've added__.

In fact, the `Session` has __identified__ that the _row returned is the same row_ as one __already represented__ within its `internal map of objects`, so we __actually got back__ the __`identical instance`__ as that which we _just added_.

The _ORM concept at work_ here is known as an __`identity map`__ and _ensures_ that __`all operations` upon a particular row within a `Session` operate upon the same set of data__. Once an object with a particular _primary key_ is __present__ in the `Session`, _all SQL queries_ on that `Session` will always __return the `same` Python object__ for that _particular primary key_; it also will __raise an error__ if an _attempt is made_ to place a _second, already-persisted object_ with the __same primary key__ _within_ the `session`.

We can _add more_ objects __at once__ using `add_all()`. Also, we've decided `Ed`'s _nickname_ isn't that great, so let's __change__ it.  The `Session` is __paying attention__. It _knows_, for example, that `Ed Jones` has been __modified__. And _three new_ `User` objects are __pending__.

We tell the `Session` that we'd like to _issue all remaining changes_ to the database and __commit the transaction__, which has been __in progress__ _throughout_. We do this via `Session.commit()`. The `Session` __emits the `UPDATE` statement__ for the _nickname change_ on `"ed"`, as well as `INSERT` statements for the _three new_ `User` objects we've __added__.

`Session.commit()` __flushes__ the _remaining changes_ to the database, and __commits the transaction__. The `connection resources` _referenced by_ the `session` are now __returned to the `connection pool`__. _Subsequent operations_ with this `session` will occur in a __new transaction__, which will again __re-acquire__ _connection resources when first needed_.

If we look at `Ed`'s _id attribute_, which _earlier_ was `None`, it __now has a value__.

After the `Session` _inserts new rows_ in the database, __all newly generated `identifiers` and `database-generated defaults` become available on the instance__, either _immediately or via load-on-first-access_. In this case, the __entire row was `re-loaded` on access__ because a _new transaction_ was begun _after_ we issued `Session.commit()`. `SQLAlchemy` _by default_ __refreshes data from a previous transaction__ the _first time it's accessed_ within a `new transaction`, so that the __most recent state__ is _available_. The _level of reloading_ is __`configurable`__ as is described in `Using the Session`.

> ##### Session Object States
> As our `User` object _moved_ from being __outside the `Session`__, to __inside the `Session`__ _without a primary key_, __to actually being inserted__, it __moved between three out of five available "object states"__ - `transient`, `pending`, and `persistent`. _Being aware of these_ __`states`__ and _what they mean_ is always a good idea - be sure to read `Quickie Intro to Object States` for a quick overview.


#### Rolling Back

Since the `Session` __works within a transaction__, we can __roll back changes made__ too. Let's make _two changes_ that we'll __revert__; `ed_user`'s user _name_ gets set to `Edwardo`, and we'll _add_ another _erroneous user_, `fake_user`.

_Querying_ the `session`, we can see that they're __flushed__ into the _current transaction_. __Rolling back__, we can see that `ed_user`'s _name_ is back to `ed`, and `fake_user` has been _kicked out_ of the `session` and _issuing_ a `SELECT` __illustrates the changes made__ to the database.


#### Querying

A `Query` object is _created_ using the `query()` method on `Session`. This function takes a _variable number of arguments_, which can be __any combination of classes__ _and_ __class-instrumented descriptors__. Below, we _indicate_ a `Query` which _loads_ `User` instances. When _evaluated_ in an __iterative context__, the _list of_ `User` _objects_ present is returned.

The `Query` also _accepts_ __ORM-instrumented descriptors__ as arguments. _Any time multiple class entities_ or _column-based entities_ are expressed as arguments to the `query()` function, the __return result is expressed as tuples__.

The _tuples_ returned by `Query` are __`named tuples`__, supplied by the `Row` class, and can be __treated much like an ordinary Python object__. The _names_ are the __same__ as the _attribute's name_ for an _attribute_, and the _class name_ for a `class`.

You __can control__ the _names of individual column expressions_ using the `ColumnElement.label()` construct, which is __available__ _from any_ `ColumnElement-derived object`, as well as any `class attribute` which is _mapped to one_ (such as `User.name`).

The name given to a _full entity_ such as `User`, _assuming_ that __multiple entities are present__ in the call to `Session.query()`, can be controlled using `aliased()`.

_Basic operations_ with `Query` include __issuing LIMIT and OFFSET__, _most conveniently_ __using Python `array slices`__ and _typically_ __in conjunction with `ORDER BY`__, and __filtering results__, which is _accomplished_ either with `filter_by()`, which _uses keyword arguments_, or `filter()`, which uses __more flexible__ `SQL expression language` constructs. These allow you to _use regular Python operators_ with the _class-level attributes_ on your `mapped class`.

The `Query` object is __fully generative__, meaning that _most method calls_ __return a new `Query` object upon which `further criteria` may be added__. For example, to _query_ for users _named_ `"ed"` with a _full name_ of `"Ed Jones"`, you can call `filter()` __twice__, which __joins criteria using `AND`__.


##### Common Filter Operators

Here's a _rundown_ of some of the _most common operators_ used in `filter()`.

* __`ColumnOperators.__eq__()`__:

```
query.filter(User.name == "ed")
```

* __`ColumnOperators.__ne__()`__:

```
query.filter(User.name != "ed")
```

* __`ColumnOperators.like()`__:

```
query.filter(User.name.like("%ed%"))
```

> ##### Note
> 
> `ColumnOperators.like()` renders the `LIKE` operator, which is __case insensitive__ on _some backends_, and __case sensitive__ on _others_. For _guaranteed_ __case-insensitive comparisons__, use `ColumnOperators.ilike()`.

* __`ColumnOperators.ilike()` (case-insensitive LIKE)__:

```
query.filter(User.name.ilike("%ed%"))
```

> ##### Note
> 
> _most backends_ __don't support `ILIKE` directly__. For those, the `ColumnOperators.ilike()` operator _renders an expression_ __combining `LIKE` with the `LOWER`__ _SQL function_ applied to each operand.

* __`ColumnOperators.in_()`__:

```
from sqlalchemy import tuple_

query.filter(User.name.in_(["ed", "wendy", "jack"]))

query.filter(User.name.in_(session.query(User.name).filter(User.name.like("%ed%"))))

query.filter(
    tuple_(User.name, User.fullname).in_([("ed", "edsnickname"), ("wendy", "windy")])
)
```

* __`ColumnOperators.not_in()`__:

```
query.filter(~User.name.in_(["ed", "wendy", "jack"]))
```

* __`ColumnOperators.is_()`__:

```
query.filter(User.name == None)

query.filter(User.name.is_(None))
```

* __`ColumnOperators.is_not()`__:

```
query.filter(User.name != None)

query.filter(User.name.is_not(None))
```

* __`AND`__:
```
from sqlalchemy import and_

query.filter(and_(User.name == "ed", User.fullname == "Ed Jones"))

query.filter(User.name == "ed", User.fullname == "Ed Jones")

query.filter(User.name == "ed").filter(User.fullname == "Ed Jones")
```

> ##### Note
> 
> Make sure you _use_ `and_()` and __not the Python `and` operator__!

* __`OR`__:

```
from sqlalchemy import or_

query.filter(or_(User.name == "ed", User.name == "wendy"))
```

> ##### Note
> 
> Make sure you _use_ `or_()` and __not the Python `or` operator__!

* __`ColumnOperators.match()`__:

```
query.filter(User.name.match("wendy"))
```

> ##### Note
> 
> `ColumnOperators.match()` uses a _database-specific_ `MATCH` or `CONTAINS` _function_; its __behavior will vary by backend__ and is __not available__ on _some backends_ such as `SQLite`.


##### Returning Lists and Scalars

A _number of methods_ on `Query` __immediately issue SQL__ and __return a value containing loaded database results__. Here's a brief tour:

* __Query.all()__ returns a _list_.

> ##### Warning
> 
> When the `Query` object _returns_ __lists of ORM-mapped objects__ such as the `User` object above, the entries are __deduplicated__ _based on_ `primary key`, as the results are __interpreted__ from the _SQL result set_. That is, if `SQL query` returns a _row_ with `id=7` _twice_, you would __only get a single `User(id=7)` object__ back in the _result list_. This __does not apply__ to the case when _individual columns_ are __queried__.

* __Query.first()__ __applies a limit of one__ and _returns_ the _first result as a scalar_.

* __Query.one()__ _fully fetches all rows_, and if __not exactly__ `one object identity` or `composite row is present` in the result, __`raises an error`__.

The `Query.one()` method is _great_ for systems that __expect to handle__ `"no items found"` versus `"multiple items found"` __differently__; such as a `RESTful web service`, which may want to raise a `"404 not found"` when __no results__ are found, but `raise an application error` when __multiple results__ are found.

* __Query.one_or_none()__ is _like_ `Query.one()`, except that _if no results are found_, it __doesn't raise an error__; it just __returns None__. Like `Query.one()`, however, it __does raise an error__ if _multiple results_ are found.

* __Query.scalar()__ _invokes_ the `Query.one()` method, and upon `success` _returns_ the __first column__ of the row.


##### Using Textual SQL

_Literal strings_ can be __used flexibly__ with `Query`, by _specifying_ their use with the `text()` construct, which is _accepted by_ __most applicable methods__. For example, `Query.filter()` and `Query.order_by()`.

_Bind parameters_ can be specified with `string-based SQL`, __using a colon__. To _specify_ the values, use the `Query.params()` method.

To use an _entirely string-based statement_, a `text()` construct _representing a complete statement_ __can be passed__ to `Query.from_statement()`. _Without further specification_, the `ORM` will __match columns__ in the _ORM mapping_ to the _result_ returned by the SQL statement based on column name.

For __better targeting__ of _mapped columns_ to a `textual SELECT`, as well as to _match_ on a _specific subset of columns_ in __arbitrary order__, _individual mapped columns_ are __passed in the desired order__ to `TextClause.columns()`.

When _selecting from_ a `text()` construct, the `Query` __may still specify__ what `columns` and `entities` are __to be returned__; _instead of_ `query(User)` we __can also ask__ for the `columns` _individually_, as in any other case.


##### Counting

`Query` includes a _convenience method_ for __counting__ called `Query.count()`.

> ##### Counting on `count()`
> 
> `Query.count()` used to be a _very complicated method_ when it would __try to guess whether or not a subquery was needed__ around the existing query, and in _some exotic cases_ it __wouldn't do the right thing__. Now that it uses a _simple subquery_ __every time__, it's _only two lines long_ and __always__ returns the `right answer`. Use `func.count()` if a particular statement __absolutely cannot tolerate__ the `subquery` _being present_.

The `Query.count()` method is used to __determine how many rows__ the SQL statement would return. Looking at the generated SQL above, `SQLAlchemy` __always places__ _whatever it is we are querying_ __into a `subquery`__, then `counts the rows` from that. In _some cases_ this __can be reduced__ to a _simpler_ `SELECT count(*) FROM table`, however _modern versions_ of `SQLAlchemy` __don't try to guess__ when this is _appropriate_, as the _exact SQL_ can be __emitted using more explicit means__.

For situations where the `"thing to be counted"` _needs to be_ __indicated specifically__, we can specify the `"count"` function __directly__ using the expression `func.count()`, _available_ from the `expression.func` construct.

__To achieve__ our _simple_ `SELECT count(*) FROM table`, we can apply it as.

The _usage_ of `Query.select_from()` __can be removed__ if we _express the count_ in terms of the `User` _primary key_ __directly__.


#### Building a Relationship

Let's consider how a _second table_, __related to `User`__, can be _mapped_ and _queried_. _Users_ in our system _can store any number of email addresses_ __associated__ with their _username_. This _implies_ a basic __one to many association__ _from the users to a new table_ which stores email addresses, which we will call `addresses`. _Using declarative_, we _define this table_ along with its __mapped class__, `Address`.

The above class introduces the `ForeignKey` construct, which is a _directive_ applied to `Column` that _indicates_ that _values in this column_ should be __constrained__ to be _values present in the named remote column_. This is a _core feature of relational databases_, and is the `"glue"` that __transforms__ an _otherwise_ __unconnected collection of tables__ to have __`rich overlapping relationships`__. The `ForeignKey` above _expresses_ that _values in the_ `addresses.user_id` _column_ should be __constrained__ to those _values in the_ `users.id` _column_, i.e. its __primary key__.

A _second directive_, known as `relationship()`, _tells the ORM_ that the `Address` class itself __should be linked__ to the `User` class, _using the attribute_ `Address.user`. `relationship()` uses the _foreign key relationships_ between the two tables to __determine the nature of this linkage__, determining that `Address.user` will be _many to one_. An _additional_ `relationship()` _directive_ is placed on the `User` _mapped class_ under the attribute `User.addresses`. _In both_ `relationship()` _directives_, the parameter `relationship.back_populates` is __assigned to refer__ to the _complementary attribute names_; by doing so, each `relationship()` can __make intelligent decision__ about the _same relationship_ as __expressed in reverse__; on one side, `Address.user` refers to a `User` instance, and on the other side, `User.addresses` refers to a __list of `Address` instances__.

> ##### Note
> 
> The `relationship.back_populates` parameter is a __newer version__ of a _very common SQLAlchemy feature_ called `relationship.backref`. The `relationship.backref` parameter __hasn't gone anywhere__ and will __always remain available__! The `relationship.back_populates` is the __same thing__, except a _little more verbose_ and _easier to manipulate_.

The _reverse side_ of a `many-to-one relationship` is __always__ `one to many`. A full catalog of available `relationship()` configurations is at `Basic Relationship Patterns`.

The _two complementing relationships_ `Address.user` and `User.addresses` are __referred__ to as a __`bidirectional relationship`__, and is a _key feature_ of the `SQLAlchemy ORM`. The section `Using the legacy 'backref' relationship parameter` discusses the `"backref"` feature in detail.

_Arguments_ to `relationship()` which _concern the remote class_ __can be specified using `strings`__, assuming the _Declarative system_ is in use. Once _all mappings_ are __complete__, these strings are __evaluated as Python expressions__ in order to _produce the actual argument_, in the above case the `User` class. The _names which are allowed during this evaluation_ include, among other things, the __names of all classes__ which have been _created in terms of the_ `declared base`.

> ##### Remember
>
> * a `FOREIGN KEY` constraint in _most (though not all)_ `relational databases` __can only link to a primary key column__, or a _column_ that has a __`UNIQUE` constraint__.
> 
> * a `FOREIGN KEY` constraint that _refers_ to a __multiple column primary key__, and _itself has multiple columns_, is known as a `"composite foreign key"`. It _can also reference_ a __subset of those columns__.
> 
> * `FOREIGN KEY` columns can __automatically update__ themselves, _in response to a change in the referenced column or row_. This is known as the __`CASCADE referential action`__, and is a _built in function_ of the `relational database`.
> 
> * `FOREIGN KEY` __can refer__ to its _own table_. This is __referred__ to as a `"self-referential"` _foreign key_.


#### Working with Related Objects

Now when we _create_ a `User`, a _blank_ `addresses` _collection_ __will be present__. _Various collection types_, such as `sets` and `dictionaries`, __are possible__ here (see `Customizing Collection Access` for details), but _by default_, the _collection_ is a __Python list__.

We are _free to add_ `Address` objects on our `User` object. In this case we just _assign a full list_ __directly__.

When using a `bidirectional relationship`, elements _added in one direction_ __automatically become visible__ in the _other direction_. _This behavior_ __occurs__ _based on_ `attribute on-change events` and is __evaluated in `Python`, without using any `SQL`__.

Let's _add and commit_ `Jack Bean` to the database. `jack` as well as the _two_ `Address` members in the _corresponding addresses collection_ are both __added to the session at once__, using a _process_ known as __`cascading`__.

_Querying_ for `Jack`, we _get just Jack back_. __No `SQL` is yet issued__ for `Jack`'s _addresses_. Let's look at the _addresses collection_. Watch the `SQL`.

When we _accessed_ the _addresses collection_, `SQL` was __suddenly issued__. This is an _example_ of a __lazy loading relationship__. The _addresses collection_ is now _loaded_ and __behaves just like an ordinary list__. We'll cover _ways to optimize the loading_ of this _collection_ in a bit.


#### Querying with Joins

Now that we have _two tables_, we can show some more features of `Query`, specifically how to _create queries_ that __deal with both tables at the same time__. The `Wikipedia` page on `SQL JOIN` offers a _good introduction to join techniques_, several of which we'll _illustrate_ here.

To construct a __simple implicit join__ between `User` and `Address`, we can use `Query.filter()` to _equate_ their _related columns together_. Below we _load_ the `User` and `Address` entities __at once__ using this method.

The actual `SQL JOIN syntax`, on the other hand, is _most easily achieved_ using the `Query.join()` method.

`Query.join()` knows _how to join_ between `User` and `Address` because there's only _one foreign key_ between them. If there were __no foreign keys, or several__, `Query.join()` __works better__ when one of the following forms are used.

The _reference documentation_ for `Query.join()` contains _detailed information_ and _examples_ of the `calling styles` accepted by this method; `Query.join()` is an _important method_ at the __center of usage for any SQL-fluent application__.

The _reference documentation_ for `Query.join()` contains _detailed information_ and _examples_ of the `calling styles` accepted by this method; `Query.join()` is an _important method_ at the __center of usage for any SQL-fluent application__.

> What does `Query` select from if there's _multiple entities_?
> 
> The `Query.join()` method will __typically join from the leftmost item__ in the _list of entities_, when the `ON clause` is _omitted_, or if the `ON clause` is a _plain SQL expression_. To __control__ the _first entity_ in the _list of JOINs_, use the `Query.select_from()` method.

```
query = session.query(User, Address).select_from(Address).join(User)
```


##### Using Aliases

When querying across _multiple tables_, if the _same table_ needs to be __referenced more than once__, `SQL` _typically requires_ that the _table_ __be aliased with another name__, so that it can be __distinguished against other occurrences__ of that `table`. This is supported using the `aliased()` construct. When _joining to relationships_ using `aliased()`, the _special attribute method_ `PropComparator.of_type()` may be used to __alter the target of a relationship join__ to _refer to a given_ `aliased()` object. Below we _join_ to the `Address` entity _twice_, to _locate_ a user who has _two distinct email addresses_ at the same time.

In addition to using the `PropComparator.of_type()` method, it is _common_ to see the `Query.join()` method _joining to a specific target by indicating it separately_.


##### Using Subqueries

The `Query` is _suitable for generating statements_ which can be used as `subqueries`. Suppose we wanted to _load_ `User` objects along with __a `count` of how many `Address` records `each user` has__. The _best way to generate SQL_ like this is to __get the count of addresses `grouped by` user ids__, and `JOIN` to the _parent_. In this case we use a `LEFT OUTER JOIN` so that we _get rows back_ for those __users who don't have any addresses__.

```
SELECT users.*, adr_count.address_count FROM users LEFT OUTER JOIN
    (SELECT user_id, count(*) AS address_count
        FROM addresses GROUP BY user_id) AS adr_count
    ON users.id=adr_count.user_id
```

Using the `Query`, we _build a statement like this_ from the __inside out__. The _statement accessor_ returns a `SQL expression` representing the __statement generated by a particular Query__ - this is an _instance_ of a `select()` construct, which are described in `SQL Expression Language Tutorial (1.x API)`.

The `func` keyword _generates SQL functions_, and the `subquery()` method on `Query` produces a _SQL expression_ construct representing a `SELECT statement` __embedded within an alias__ (it's _actually_ __shorthand__ for `query.statement.alias()`).

Once we have our statement, it behaves like a `Table` construct, such as the one we created for users at the start of this tutorial. The _columns on the statement_ are __accessible__ through an _attribute_ called `c`.


##### Selecting Entities from Subqueries

Above, we just __selected a result__ that _included a column_ from a `subquery`. What if we wanted our `subquery` to _map to an entity_? For this we use `aliased()` to __associate__ an `"alias"` of a _mapped class_ to a `subquery`.


##### Using EXISTS

The `EXISTS` keyword in `SQL` is a __boolean operator__ which _returns_ `True` if the _given expression_ __contains any rows__. It _may be used_ in many scenarios _in place of joins_, and is also _useful for locating rows_ which __do not have a corresponding row__ in a `related table`.

The `Query` features _several operators_ which __make usage of `EXISTS` automatically__. Above, the `statement` can be _expressed_ along the `User.addresses` _relationship_ using `Comparator.any()`.

`Comparator.any()` takes _criterion_ as well, to __limit the rows matched__.

`Comparator.has()` is the _same operator_ as `Comparator.any()` __for many-to-one relationships__ (note the `~` operator here too, which means `"NOT"`).


##### Common Relationship Operators

Here's all the _operators_ which build on `relationships`:

* `Comparator.__eq__()` (many-to-one "equals" comparison):

```
query.filter(Address.user == someuser)
```

* `Comparator.__ne__()` (many-to-one "not equals" comparison):

```
query.filter(Address.user != someuser)
```

* `IS NULL` (many-to-one comparison, also uses `Comparator.__eq__()`):

```
query.filter(Address.user == None)
```

* `Comparator.contains()` (used for one-to-many collections):

```
query.filter(User.addresses.contains(someaddress))
```

* `Comparator.any()` (used for collections):

```
query.filter(User.addresses.any(Address.email_address == "bar"))

# also takes keyword arguments:

query.filter(User.addresses.any(Address.email_address="bar"))
```

* `Comparator.has()` (used for scalar references):

```
query.filter(Address.user.has(name="ed"))
```

* `Query.with_parent()` (used for any relationship):

```
session.query(Address).with_parent(someuser, "addresses")
```


#### Eager Loading

Recall earlier that we illustrated a __lazy loading__ operation, when we accessed the `User.addresses` collection of a `User` and SQL was emitted. If you want to _reduce_ the number of queries (__dramatically__, in _many cases_), we can apply an __eager load__ to the query operation. `SQLAlchemy` offers __three types of `eager loading`__, _two_ of which are __automatic__, and a _third_ which __involves custom criterion__. _All three_ are usually __invoked via functions__ known as `query options` which give _additional instructions_ to the `Query` on how we would like various _attributes_ to be __loaded__, via the `Query.options()` method.


##### Selectin Load

In this case we'd like to indicate that `User.addresses` should _load eagerly_. _A good choice_ for `loading a set of objects` as well as their `related collections` is the `selectinload()` option, which __emits a second `SELECT` statement__ that _fully loads_ the `collections associated` with the __results just loaded__. The name __`"selectin"`__ _originates_ from the fact that the `SELECT` statement uses an `IN clause` in order to _locate related rows_ for __multiple objects at once__.


##### Joined Load

The other __automatic__ _eager loading function_ is _more well known_ and is called `joinedload()`. This _style of loading_ __emits__ a `JOIN`, _by default_ a `LEFT OUTER JOIN`, so that the _lead object_ as well as the _related object_ or _collection_ is __loaded in one step__. We illustrate loading the same addresses collection in this way - note that even though the `User.addresses` collection on _jack_ is actually populated right now, the query will __emit the extra join regardless__.

Note that even though the `OUTER JOIN` resulted in _two rows_, we still __only got `one` instance of User__ back. This is because `Query` applies a `"uniquing"` strategy, __based on object identity__, to the _returned entities_. This is _specifically_ so that `joined eager loading` can be applied __without affecting the query results__.

While `joinedload()` has been around for a long time, `selectinload()` is a _newer form_ of __eager loading__. `selectinload()` tends to be _more appropriate_ for __loading related collections__ while `joinedload()` tends to be _better suited_ for __many-to-one relationships__, due to the fact that __only one row__ is _loaded_ for both the _lead_ and the _related_ object. Another form of loading, `subqueryload()`, _also exists_, which can be used in place of `selectinload()` when making use of __composite primary keys__ on certain backends.

> ##### joinedload() is not a replacement for join()
> 
> The join created by `joinedload()` is __anonymously aliased__ such that it __does not affect the query results__. An `Query.order_by()` or `Query.filter()` call __cannot reference__ these _aliased tables_ - so-called `"user space"` joins are constructed using `Query.join()`. The _rationale_ for this is that `joinedload()` is __only applied__ in order to affect _how related objects or collections are loaded_ as an __optimizing detail__ - it can be _added_ or _removed_ with __no impact on actual results__. See the section `The Zen of Joined Eager Loading` for a detailed description of how this is used.


##### Explicit Join + Eagerload

A _third_ style of _eager loading_ is when we are _constructing_ a `JOIN` __explicitly__ in order to __locate the primary rows__, and would like to _additionally_ apply the _extra table_ to a `related object` or `collection` on the _primary object_. This feature is supplied via the `contains_eager()` function, and is _most typically_ __useful for pre-loading the many-to-one object__ on a _query_ that __needs to filter on that same object__. Below we illustrate loading an `Address` row as well as the _related User object_, __filtering__ on the `User` named `"jack"` and using `contains_eager()` to apply the `"user"` columns to the `Address.user` attribute.


#### Deleting

Let's try to `delete` _jack_ and see how that goes. We'll __mark the object as deleted__ in the `session`, then we'll _issue a count query_ to see that __no rows remain__.

So far, so good. How about _Jack_'s `Address` objects? Uh oh, they're __still there__! Analyzing the `flush SQL`, we can see that the `user_id` column of _each address_ was __set to `NULL`__, but the __rows weren't deleted__. `SQLAlchemy` __doesn't assume that deletes cascade__, you have to tell it to do so.


##### Configuring delete/delete-orphan Cascade

We will _configure_ __cascade options__ on the `User.addresses` _relationship_ to change the behavior. While `SQLAlchemy` allows you to _add new attributes and relationships to mappings_ at any point in time, in this case the __existing relationship needs to be removed__, so we need to __tear down the mappings completely__ and _start again_ - we'll __close__ the `Session` and _use_ a __new__ `declarative_base()`.

Next we'll _declare_ the `User` class, adding in the `addresses` _relationship_ including the __cascade configuration__ (we'll leave the constructor out too).

Now when we _load_ the user _jack_ (below using `Query.get()`, which __loads by primary key__), _removing an address from the corresponding addresses collection_ will result in that `Address` being __deleted__.

_Deleting Jack_ will `delete` __both Jack and the `remaining` Address__ _associated_ with the _user_.


#### Building a Many To Many Relationship

We're moving into the _bonus round_ here, but lets show off a `many-to-many relationship`. We'll sneak in _some other features_ too, just to take a tour. We'll make our application a _blog application_, where _users_ can __write `BlogPost` items__, which have `Keyword` items __associated__ with them.

For a _plain_ `many-to-many`, we need to _create_ an __un-mapped `Table` construct__ to _serve_ as the __association table__.

Above, we can see _declaring_ a `Table` __directly__ is a __little different__ than _declaring_ a `mapped class`. `Table` is a _constructor function_, so each individual `Column` argument is __separated by a comma__. The `Column` object is also given its `name` __explicitly__, rather than it being taken from an assigned attribute name.

Next we define `BlogPost` and `Keyword`, using _complementary_ `relationship()` constructs, _each referring_ to the `post_keywords` table as an __association table__.

> ##### Note
> 
> The above class declarations illustrate explicit `__init__()` methods. Remember, when using `Declarative`, it's __optional__!

Above, the _many-to-many relationship_ is `BlogPost.keywords`. The defining feature of a _many-to-many relationship_ is the `secondary` keyword argument which _references_ a `Table` object representing the __association table__. This table _only_ contains `columns` which reference the __two sides of the relationship__; if it has _any other columns_, such as its __own primary key__, or _foreign keys_ to `other tables`, `SQLAlchemy` __requires__ a _different usage pattern_ called the __`"association object"`__, described at `Association Object`.

We would also like our `BlogPost` class to have an _author_ field. We will _add_ this as another __bidirectional relationship__, except _one issue_ we'll have is that a _single user might have lots of blog posts_. When we access `User.posts`, we'd like to be able to __filter results further__ so as _not to load_ the `entire collection`. For this we use a _setting_ accepted by `relationship()` called __lazy='dynamic'__, which _configures_ an __alternate loader strategy__ on the attribute.

_Usage_ is __not too different__ from what we've been doing. Let's give `Wendy` some _blog posts_.

We're _storing keywords uniquely_ in the database, but we know that we __don't have any yet__, so we can just _create_ them.

We __can now look up__ _all blog posts_ with the _keyword_ `"firstpost"`. We'll use the _any operator_ to locate `blog posts where any of its keywords has the keyword string "firstpost"`.

If we want to __look up__ _posts owned by the user_ `wendy`, we can tell the _query_ to __narrow down__ to that `User` object as a _parent_.

Or we can use `Wendy`'s _own posts relationship_, which is a __`"dynamic"` relationship__, to query straight from there.
