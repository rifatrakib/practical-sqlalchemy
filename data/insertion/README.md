## Inserting Rows with Core

When using _Core_, a `SQL INSERT statement` is generated using the `insert()` function - this function generates a new instance of `Insert` which represents an `INSERT statement` in __SQL__, that _adds new data into a table_.

> __ORM Readers__ - The way that rows are `INSERT`ed into the database from an ORM perspective makes use of _object-centric APIs_ on the `Session` object known as the _unit of work process_, and is fairly __different from the Core-only approach__ described here. The more ORM-focused sections later starting at Inserting Rows with the ORM subsequent to the Expression Language sections introduce this.

#### The `insert()` SQL Expression Construct

A simple example of `Insert` illustrating the `target table` and the `VALUES clause` at once.

The above _stmt variable_ is an instance of `Insert`. Most SQL expressions can be stringified in place as a means to see the general form of what's being produced.

The _stringified_ form is created by producing a `Compiled` form of the object which includes a __database-specific string SQL representation__ of the statement; we can acquire this object directly using the `ClauseElement.compile()` method.

Our `Insert` construct is an example of a `"parameterized" construct`; to view the `name` and `fullname` _bound parameters_, these are available from the `Compiled` construct as well.

#### Executing the Statement

Invoking the statement we can _INSERT a row into `user_table`_. The `INSERT SQL` as well as the _bundled parameters_ can be seen in the `SQL logging`.

In its simple form above, _the `INSERT statement` does not return any rows_, and if `only a single row` is inserted, it will _usually include_ the ability to _return information about column-level default values_ that were generated during the `INSERT` of that row, most commonly an integer primary key value. In the above case the first row in a SQLite database will normally return 1 for the first integer primary key value, which we can acquire using the `CursorResult.inserted_primary_key` accessor.

> __CursorResult.inserted_primary_key__ returns a `tuple` because _a primary key may contain multiple columns_. This is known as a __composite primary key__. The `CursorResult.inserted_primary_key` is intended to always contain the _complete primary key_ of the record _just inserted_, not just a `cursor.lastrowid` kind of value, and is also intended to be populated regardless of whether or not `autoincrement` were used, hence _to express a complete primary key it's a tuple_.

> From version 1.4.8, the tuple returned by `CursorResult.inserted_primary_key` is now a __named tuple__ fulfilled by returning it as a `Row` object.

#### `INSERT` usually generates the "values" clause automatically

The example above made use of the `Insert.values()` method to _explicitly_ create the `VALUES` clause of the `SQL INSERT statement`. This method in fact has some variants that allow for special forms such as _multiple rows in one statement_ and insertion of SQL expressions. However the usual way that `Insert` is used is such that the `VALUES clause` is _generated automatically_ from the parameters passed to the `Connection.execute()` method; below we `INSERT` two more rows to illustrate this.

The execution above features `executemany` form, however unlike when using the `text()` construct, we _didn't have to spell out any SQL_. By passing _a dictionary or list of dictionaries_ to the `Connection.execute()` method in conjunction with the `Insert` construct, the `Connection` ensures that the column names which are passed will be expressed in the `VALUES` clause of the `Insert` construct __automatically__.

> ##### Deep Alchemy
>
> Towards the goal of having some interesting data in the `address_table` as well, below is a more advanced example illustrating how the `Insert.values()` method may be used __explicitly__ while at the same time _including for additional VALUES generated from the parameters_. A __scalar subquery__ is constructed, making use of the `select()` construct introduced in the next section, and the parameters used in the _`subquery`_ are set up using an _explicit bound parameter `name`_, established using the `bindparam()` construct.

#### INSERT...FROM SELECT

The `Insert` construct can compose an `INSERT` that gets rows _directly from a **SELECT**_ using the `Insert.from_select()` method.

#### INSERT...RETURNING

The `RETURNING` clause for supported backends is used __automatically__ in order to _retrieve the last inserted primary key value as well as the values for server defaults_. However the `RETURNING` clause _may_ also be __specified explicitly__ using the `Insert.returning()` method; in this case, the `Result` object that's returned when the statement is executed has rows which can be fetched.

The `RETURNING` feature is __also supported__ by _UPDATE and DELETE statements_, which will be introduced later in this tutorial. The `RETURNING` feature is generally __only supported__ for statement executions that use __`a single set of bound parameters`__; that is, it _wont work with the executemany_ form. Additionally, some dialects such as the _`Oracle dialect` only allow RETURNING to return a single row overall_, meaning it won't work with `"INSERT...FROM SELECT"` nor will it work with `multiple row Update or Delete` forms.

There is _internal support_ for the `psycopg2` dialect to __INSERT many rows at once and also support RETURNING__, which is leveraged by the SQLAlchemy ORM. However this feature has _not been generalized_ to all dialects and is not yet part of SQLAlchemy's regular API.
