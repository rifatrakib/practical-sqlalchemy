## Working with Transactions and the DBAPI

With the `Engine` object ready to go, we may now proceed to dive into the basic operation of an `Engine` and its primary interactive endpoints, the `Connection` and `Result`. We will additionally introduce the `ORM`'s facade for these objects, known as the `Session`.

> When using the ORM, the `Engine` is managed by another object called the `Session`. The `Session` in modern SQLAlchemy emphasizes a transactional and SQL execution pattern that is largely identical to that of the `Connection` discussed below, so while this subsection is Core-centric, all of the concepts here are essentially relevant to ORM use as well and is recommended for all ORM learners. The execution pattern used by the `Connection` will be contrasted with that of the `Session` at the end of this section.

#### Getting a Connection

The sole purpose of the `Engine` object from a user-facing perspective is to provide a unit of connectivity to the database called the `Connection`. When working with the Core directly, the `Connection` object is how all interaction with the database is done. As the `Connection` represents an open resource against the database, we want to always limit the scope of our use of this object to a specific context, and the best way to do that is by using `Python context manager` form, also known as the `with statement`.

In this example, the context manager provided for a database connection and also framed the operation inside of a transaction. The default behavior of the `Python DBAPI` includes that **a transaction is always in progress**; when the scope of the connection is released, a __ROLLBACK__ is emitted to end the transaction. The transaction is _not committed_ automatically; when we want to commit data we normally need to call `Connection.commit()`.

> `autocommit` mode is available for special cases.

The result of our `SELECT` was also returned in an object called `Result` that will be discussed later, however for the moment we'll add that it's best to ensure this object is consumed within the `connect` block, and is not passed along outside of the scope of our connection.


#### Committing Changes

As learnt already that the `DBAPI connection is non-autocommitting`, what if we want to commit some data? We can create a table and insert some data, and the transaction is then committed using the `Connection.commit()` method, invoked inside the block where we acquired the `Connection` object.

In this example, the two SQL statements that are generally `transactional`, a `CREATE TABLE statement` and an `INSERT statement` that's parameterized. As we want the work we've done to be committed (saved) within our block, we invoke the `Connection.commit()` method which commits the transaction. After we call this method inside the block, we can continue to run more SQL statements and if we choose we may call `Connection.commit()` again for subsequent statements. SQLAlchemy refers to this style as **commit as you go**.

There is also another style of committing data, which is that we can declare our `connect` block to be a transaction block up front. For this mode of operation, we use the `Engine.begin()` method to acquire the connection, rather than the `Engine.connect()` method. This method will both manage the scope of the `Connection` and also enclose everything inside of a transaction with `COMMIT at the end, assuming a successful block`, or `ROLLBACK in case of exception raise`. This style may be referred towards as **begin once**.

> `Begin once` style is often preferred as it is more succinct and indicates the intention of the entire block up front.

> ##### What’s `BEGIN (implicit)`?
> You might have noticed the log line `BEGIN (implicit)` at the start of a transaction block. `implicit` here means that SQLAlchemy did not actually send any command to the database; it just considers this to be the start of the DBAPI's implicit transaction. You can register event hooks to intercept this event, for example.

#### Basics of Statement Execution

A few examples has been demonstrated that run SQL statements against a database, making use of a method called `Connection.execute()`, in conjunction with an object called `text()`, and returning an object called `Result`. In this section we'll illustrate more closely the mechanics and interactions of these components.

> Most of the content in this section applies equally well to modern ORM use when using the `Session.execute()` method, which works very similarly to that of `Connection.execute()`, including that ORM result rows are delivered using the same `Result` interface used by Core.

The `SELECT` string we executed selected all rows from our table. The object returned is called `Result` and represents an iterable object of result rows.

`Result` has lots of methods for fetching and transforming rows, such as the `Result.all()` method illustrated previously, which returns a list of all `Row` objects. It also implements the `Python iterator interface` so that we can iterate over the collection of Row objects directly.

The `Row` objects themselves are intended to act like Python `named tuples`. Later we illustrate a variety of ways to access rows.

* __Tuple Assignment__ - This is the most `Python-idiomatic style`, which is to assign variables to each row positionally as they are received:

```
result = conn.execute(text("SELECT x, y FROM table_name"))
for x, y in result:
    # do something here ...
```

* __Integer Index__ - Tuples are Python sequences, so regular integer access is available too:

```
result = conn.execute(text("SELECT x, y FROM table_name"))
for row in result:
    x = row[0]
```

* __Attribute Name__ - As these are Python named tuples, the tuples have `dynamic attribute names matching the names of each column`. These names are normally the names that the SQL statement assigns to the columns in each row. While they are usually fairly predictable and can also be controlled by labels, in less defined cases they may be subject to database-specific behaviors:

```
result = conn.execute(text("SELECT x, y FROM table_name"))
for row in result:
    x = row.x
    # illustrate use with Python f-strings
    print(f"Row: x {row.y}")
```

* __Mapping Access__ - To receive rows as Python `mapping objects`, which is essentially a read-only version of Python's interface to the common `dict` object, the `Result` may be transformed into a `MappingResult` object using the `Result.mappings()` modifier; this is a result object that yields dictionary-like `RowMapping` objects rather than `Row` objects:

```
result = conn.execute(text("select x, y from some_table"))
for dict_row in result.mappings():
    x = dict_row['x']
    y = dict_row['y']
```

#### Sending Parameters

`SQL statements` are usually accompanied by data that is to be passed with the statement itself, as we saw in the `INSERT` example previously. The `Connection.execute()` method therefore also accepts parameters, which are referred towards as __bound parameters__. A rudimentary example might be if we wanted to limit our `SELECT statement` only to rows that meet a certain criteria, such as rows where the `"y"` value were greater than a certain value that is passed in to a function.

In order to achieve this such that the `SQL statement` can remain fixed and that the driver can `properly sanitize` the value, we add a `WHERE criteria` to our statement that names a new parameter called `"y"`; the `text()` construct accepts these using a colon format `":y"`. The actual value for `":y"` is then passed as the second argument to `Connection.execute()` in the form of a dictionary.

In the logged SQL output, we can see that the bound parameter `":y"` was converted into a `question mark` when it was sent to the SQLite database. This is because the SQLite database driver uses a format called `"qmark parameter style"`, which is one of `six different formats` allowed by the `DBAPI specification`. SQLAlchemy abstracts these formats into just one, which is the `named` format using a colon.

> ##### Always use bound parameters
>
> As mentioned at the beginning of this section, textual SQL is not the usual way we work with SQLAlchemy. However, when using textual SQL, __a Python literal value, even non-strings like integers or dates, should never be stringified into SQL string directly__; a parameter should always be used. This is most famously known as _how to avoid SQL injection attacks_ when the data is untrusted. However it also allows the SQLAlchemy dialects and/or DBAPI to correctly handle the incoming input for the backend. Outside of plain textual SQL use cases, SQLAlchemy's Core Expression API otherwise ensures that Python literal values are passed as bound parameters where appropriate.

#### Sending Multiple Parameters

In the example at Committing Changes, we executed an INSERT statement where it appeared that we were able to _INSERT multiple rows into the database at once_. For statements that operate upon data, but _do not return result sets_, namely `DML statements` such as `INSERT` which don’t include a phrase like `RETURNING`, we can send multi params to the `Connection.execute()` method by passing a list of dictionaries instead of a single dictionary, thus allowing the __single SQL statement to be invoked against each parameter set__ individually.

Behind the scenes, the `Connection` objects uses a `DBAPI feature` known as `cursor.executemany()`. This method performs the equivalent operation of invoking the given SQL statement against each parameter set individually. The DBAPI _may optimize_ this operation in a variety of ways, __by using prepared statements__, or __by concatenating the parameter sets into a single SQL statement__ in some cases. Some SQLAlchemy dialects _may also use alternate APIs_ for this case, such as the `psycopg2 dialect for PostgreSQL` which uses _more performant APIs_ for this use case.

> This section isn't part of the ORM. That's because the `multiple parameters` use case is usually used for `INSERT statements`, which when using the ORM are invoked in a different way. Multiple parameters also may be used with `UPDATE and DELETE statements` to _emit distinct UPDATE/DELETE operations on a per-row basis_, however again when using the ORM, there is a different technique generally used for updating or deleting many individual rows separately.


#### Executing with an ORM Session

As mentioned previously, most of the patterns and examples above apply to use with the ORM as well, so here we will introduce this usage so that as the tutorial proceeds, we will be able to illustrate each pattern in terms of Core and ORM use together.

The fundamental `transactional/database interactive object` when using the ORM is called the `Session`. In modern SQLAlchemy, this object is used in a manner very similar to that of the `Connection`, and in fact as the `Session` is used, it refers to a `Connection` internally which it uses to emit SQL.

When the `Session` is used with non-ORM constructs, it passes through the SQL statements we give it and does not generally do things much differently from how the `Connection` does directly, so we can illustrate it here in terms of the simple textual SQL operations we've already learned.

The `Session` has a few different creational patterns, but here we will illustrate the most basic one that tracks exactly with how the `Connection` is used which is to construct it within a `context manager`.

The example above can be compared to the example in the preceding section in `Sending Parameters` - we directly replace the call to `with engine.connect() as conn` with `with Session(engine) as session`, and then make use of the `Session.execute()` method just like we do with the `Connection.execute()` method.

Also, like the `Connection`, the `Session` features `commit as you go` behavior using the `Session.commit()` method.

Above, we invoked an `UPDATE statement` using the bound-parameter, `executemany` style of execution introduced at `Sending Multiple Parameters`, ending the block with a `commit as you go` commit.

The `Session` doesn't actually hold onto the `Connection` object after it _ends the transaction_. It gets a __new `Connection`__ from the `Engine` when executing SQL against the database is next needed.

The `Session` obviously has a lot more tricks up its sleeve than that, however understanding that it has a `Session.execute()` method that's used the same way as `Connection.execute()` will get us started with the examples that follow later.
