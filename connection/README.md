## Establishing Connectivity - the Engine

The start of any SQLAlchemy application is an object called the `Engine`. This object acts as a central source of connections to a particular database, providing both a factory as well as a holding space called a `connection pool` for these database connections. The engine is typically a global object created just once for a particular database server, and is configured using a URL string which will describe how it should connect to the database host or backend.

For this tutorial an in-memory-only SQLite database is used. This is an easy way to test things without needing to have an actual pre-existing database set up. The Engine is created by using `create_engine()`, specifying the `create_engine.future` flag set to True so that we make full use of `2.0 style` usage:

The main argument to `create_engine` is a string URL, above passed as the string `"sqlite+pysqlite:///:memory:"`. This string indicates to the Engine three important facts:

1. What kind of database are we communicating with? This is the sqlite portion above, which links in SQLAlchemy to an object known as the dialect (specific database application).

2. What `DBAPI` are we using? `The Python DBAPI` is a third party driver that SQLAlchemy uses to interact with a particular database. In this case, we’re using the name `pysqlite`, which in modern Python use is the `sqlite3` standard library interface for SQLite. If omitted, SQLAlchemy will use a default `DBAPI` for the particular database selected.

3. How do we locate the database? In this case, our URL includes the phrase `/:memory:`, which is an indicator to the sqlite3 module that we will be using an **in-memory-only** database. This kind of database is perfect for experimenting as it does not require any server nor does it need to create new files.

> A parameter `create_engine.echo` can also be specified, which will instruct the Engine to log all of the SQL it emits to a `Python logger` that will write to standard out. This flag is a shorthand way of setting up Python logging more formally and is useful for experimentation in scripts. Many of the SQL examples will include this SQL logging output beneath a `[SQL]` link that when clicked, will reveal the full SQL interaction.


#### Lazy Connecting

The `Engine`, when first returned by `create_engine()`, has not actually tried to connect to the database yet; that happens only the first time it is asked to perform a task against the database. This is a software design pattern known as `lazy initialization`.
