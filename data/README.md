## Working with Data

In Working with `Transactions` and the `DBAPI`, we learned the basics of how to interact with the Python DBAPI and its transactional state. Then, in Working with `Database Metadata`, we learned how to _represent database tables, columns, and constraints_ within SQLAlchemy using the _`MetaData` and related objects_. In this section we will combine both concepts above to _create, select and manipulate data_ within a `relational database`. Our interaction with the database is __always__ in terms of a _`transaction`_, even if we've set our database driver to use _autocommit_ behind the scenes.

The components of this section are as follows:

* __Inserting Rows with Core__ - to get some data into the database, we introduce and demonstrate the `Core Insert construct`. _INSERTs from an ORM perspective_ are described in the next section `Data Manipulation with the ORM`.

* __Selecting Rows with Core or ORM__ - this section will describe in detail the `Select construct`, which is the most commonly used object in SQLAlchemy. The `Select construct` _emits SELECT statements_ for both Core and ORM centric applications and both use cases will be described here. Additional ORM use cases are also noted in the later section Using `Relationships` in Queries as well as the `ORM Querying Guide`.

* __Updating and Deleting Rows with Core__ - Rounding out the `INSERT and SELECT`ion of data, this section will describe from a Core perspective the use of the `Update and Delete constructs`. _ORM-specific_ `UPDATE and DELETE` is similarly described in the `Data Manipulation with the ORM` section.
