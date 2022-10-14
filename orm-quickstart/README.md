## Declare Models

Here, we define _module-level_ constructs that will __form the structures__ which we will be `querying` from the database. This structure, known as a `Declarative Mapping`, _defines at once_ both a __Python object model__, as well as __database metadata__ that _describes real SQL tables_ that `exist, or will exist`, in a particular database.

The _mapping_ starts with a `base class`, which above is called `Base`, and is created by calling upon the `declarative_base()` function, which produces a __new `base` class__.

_Individual mapped classes_ are then _created_ by making __subclasses of `Base`__. A _mapped class_ typically refers to a `single particular database table`, the name of which is indicated by using the __`__tablename__`__ _class-level attribute_.

Next, _columns_ that are part of the table are declared, by _adding attributes_ __linked__ to the `Column` construct. `Column` describes _all aspects_ of a `database column`, including __typing information__ with _type objects_ such as `Integer` and `String` as well as __server defaults__ and __constraint information__, such as _membership_ within the `primary key` and `foreign keys`.

_All_ `ORM mapped classes` __require__ _at least_ __one column__ be declared as part of the `primary key`, typically by using the `Column.primary_key` parameter on those `Column` objects that should be part of the key. In the above example, the `User.id` and `Address.id` columns are _marked_ as __primary key__.

Taken together, the _combination_ of a `string table name` as well as a `list of column declarations` is __referred__ towards in SQLAlchemy as __`table metadata`__. Setting up `table metadata` using both `Core` and `ORM` approaches is introduced in the `SQLAlchemy 1.4/2.0 Tutorial` at `Working with Database Metadata`. The above mapping is an example of what's referred towards as `Declarative Table configuration`.

Other _Declarative directives_ are available, most commonly the `relationship()` construct indicated above. In contrast to the _column-based attributes_, `relationship()` denotes a __linkage between two `ORM classes`__. In the above example, `User.addresses` __links `User` to `Address`__, and `Address.user` __links `Address` to `User`__. The `relationship()` construct is introduced in the `SQLAlchemy 1.4/2.0 Tutorial` at `Working with Related Objects`.

Finally, the above example classes include a `__repr__()` method, which is _not required_ but is __useful for debugging__.


## Create an Engine

The `Engine` is a _factory_ that can __create new database connections__ for us, which also _holds onto connections_ inside of a `Connection Pool` for __fast reuse__. For learning purposes, we normally use a `SQLite` __memory-only__ database for convenience.

> ##### Tips
> 
> The `echo=True` parameter indicates that __SQL emitted by connections__ will be _logged to standard out_. `future=True` is to __ensure__ we are using the _latest SQLAlchemy 2.0-style APIs_.


## Emit CREATE TABLE DDL

Using our `table metadata` and our `engine`, we can _generate_ our `schema` __at once__ in our __target `SQLite` database__, using a method called `MetaData.create_all()`.


## Create Objects and Persist

We are now ready to `insert` data in the database. We accomplish this by _creating instances_ of `User` and `Address` classes, which have an `__init__()` method already as __established automatically__ by the __`declarative mapping process`__. We then _pass them to the database_ using an object called a `Session`, which makes use of the `Engine` to __interact with the `database`__. The `Session.add_all()` method is used here to __add multiple objects at once__, and the `Session.commit()` method will be used to __flush any pending changes__ to the database and then __commit__ the _current database transaction_, which is __always in progress__ whenever the `Session` is used.

> ##### Tips
> 
> It's recommended that the `Session` be __used in context manager style__ as above, that is, using the Python `with: statement`. The `Session` object __represents__ _active database resources_ so it's good to make sure it's __closed out__ when a _series of operations_ are __`completed`__. In the next section, we'll keep a `Session` opened just for illustration purposes.


## Simple SELECT

With some rows in the database, here's the _simplest form_ of __emitting__ a `SELECT` statement _to load some objects_. To create `SELECT` statements, we use the `select()` function to __create a new `Select` object__, which we then _invoke_ using a `Session`. The method that is _often useful_ when __querying for `ORM` objects__ is the `Session.scalars()` method, which will return a `ScalarResult` object that will _iterate_ through the ORM objects we've selected.

The query can also make use of the `Select.where()` method to __add `WHERE` criteria__, and also used the `ColumnOperators.in_()` method that's part of all SQLAlchemy _column-like constructs_ to use the SQL `IN operator`.


## SELECT with JOIN

It's _very common_ to `query` amongst __multiple tables at once__, and in SQL the `JOIN` _keyword_ is the _primary way_ this happens. The `Select` construct __creates joins__ using the `Select.join()` method.

The above query illustrates __multiple `WHERE` criteria__ which are __automatically chained together__ using `AND`, as well as how to use SQLAlchemy _column-like objects_ to __create `"equality"` comparisons__, which uses the _overridden_ Python method `ColumnOperators.__eq__()` to produce a _SQL criteria object_.


## Make Changes

The `Session` object, in conjunction with our _ORM-mapped classes_ `User` and `Address`, __automatically track changes to the objects__ as they are made, which result in _SQL statements_ that will be __emitted the next time the `Session` flushes__. Below, we _change_ one `email address` _associated_ with `"sandy"`, and also __add a new email address__ to `"patrick"`, _after emitting_ a `SELECT` to __retrieve the row for `"patrick"`__.

Notice when we accessed `patrick.addresses`, a `SELECT` was _emitted_. This is called a __`lazy load`__. Background on different ways to _access related items_ using more or less SQL is introduced at `Loader Strategies`.


## Some Deletes

All things must come to an end, as is the case for some of our database rows - here's a quick demonstration of __two different forms of `deletion`__, both of which are _important based on the specific use case_.

First we will _remove_ one of the `Address` objects from the `"sandy"` user. When the `Session` _next flushes_, this will __result in the row being deleted__. This behavior is something that we _configured in our mapping_ called the __`delete cascade`__. We can get a handle to the `sandy` object by _primary key_ using `Session.get()`, then work with the object.

The _last_ `SELECT` above was the __`lazy load`__ operation proceeding so that the `sandy.addresses` collection could be _loaded_, so that we could _remove_ the `sandy_address` member. There are _other ways_ to go about this _series of operations_ that _won't emit as much SQL_.

We can _choose to emit_ the `DELETE` SQL for what's _set to be changed so far_, __without committing the transaction__, using the `Session.flush()` method.

Next, we will _delete_ the `"patrick"` user _entirely_. For a _top-level delete_ of an object by itself, we use the `Session.delete()` method; this method __doesn't actually perform the deletion__, but __sets up the object to be deleted__ on the _next flush_. The operation will __also cascade to related objects__ _based on the cascade_ options that we _configured_, in this case, onto the _related `Address` objects_.

The `Session.delete()` method in this particular case __emitted two `SELECT` statements__, even though it __didn't emit a DELETE__, which _might seem surprising_. This is because when the method went to inspect the object, it turns out the `patrick` object was __expired__, which happened when we _last called upon_ `Session.commit()`, and the SQL __emitted__ was to __re-load the rows__ from the `new transaction`. This `expiration` is _optional_, and in normal use we will often be turning it off for situations where it doesn't apply well.
