## Updating and Deleting Rows with Core

So far we've covered `Insert`, so that we can get some data into our database, and then spent a lot of time on `Select` which _handles the broad range of usage patterns_ used for __retrieving data from the database__. In this section we will cover the `Update` and `Delete` constructs, which are used to __modify existing rows__ as well as __delete existing rows__. This section will cover these constructs from a _Core-centric perspective_.

> `ORM Readers` - As was the case mentioned at `Inserting Rows with Core`, the `Update` and `Delete` operations when used _with the ORM_ are usually __invoked internally from the Session object__ as part of the unit of work process.
>
> However, __unlike Insert__, the `Update` and `Delete` constructs __can also be used directly with the ORM__, using a pattern known as __`"ORM-enabled update and delete"`__; for this reason, familiarity with these constructs is useful for ORM use. Both styles of use are discussed in the sections `Updating ORM Objects` and `Deleting ORM Objects`.


#### The `update()` SQL Expression Construct

The `update()` function generates a _new instance of Update_ which represents an `UPDATE` statement in SQL, that will __update existing data in a table__. Like the `insert()` construct, there is a `"traditional"` form of `update()`, which __emits `UPDATE` against a single table__ at a time and __`does not` return any rows__. However _some backends_ support an `UPDATE` statement that __may modify multiple tables at once__, and the `UPDATE` statement also supports `RETURNING` such that _columns contained in matched rows may be returned in the result set_.

The `Update.values()` method __controls the contents of the SET elements__ of the `UPDATE` statement. This is the __same method shared by the `Insert` construct__. Parameters can normally be _passed using the column names as keyword arguments_. `UPDATE` _supports all the major SQL forms_ of `UPDATE`, __including updates against expressions__, where we can make use of `Column` expressions.

To support `UPDATE` in an __`"executemany"`__ context, where many parameter sets will be invoked against the same statement, the `bindparam()` construct may be used to __set up bound parameters__; these __replace the places__ that _literal values would normally go_.


##### Correlated Updates

An `UPDATE` statement can _make use of rows in other tables_ by using a __correlated subquery__. A `subquery` may be used _anywhere a column expression might be placed_.


##### UPDATE ... FROM

_Some databases_ such as `PostgreSQL` and `MySQL` support a syntax `"UPDATE FROM"` where _additional tables may be stated directly_ in a __special FROM clause__. This syntax will be __generated implicitly__ when additional tables are located in the `WHERE` clause of the statement.

There is also a `MySQL` specific syntax that __can `UPDATE` multiple tables__. This __requires__ we refer to `Table` objects in the `VALUES` clause in order to _refer to additional tables_.


##### Parameter Ordered Updates

Another _`MySQL`-only behavior_ is that the _order of parameters_ in the `SET clause` of an `UPDATE` actually __impacts the evaluation of each expression__. For this use case, the `Update.ordered_values()` method accepts a _sequence of tuples_ so that this __order may be controlled__.

While `Python dictionaries` are __guaranteed to be insert ordered__ as of Python 3.7, the `Update.ordered_values()` method still _provides an additional measure of clarity of intent_ when it is __essential__ that the `SET clause` of a `MySQL` `UPDATE` statement proceed in a specific way.


#### The `delete()` SQL Expression Construct

The `delete()` function _generates a new instance of Delete_ which represents a `DELETE` statement in SQL, that will __delete rows from a table__. The `delete()` statement from an _API perspective_ is __very similar__ to that of the `update()` construct, traditionally _returning no rows_ but __allowing for a RETURNING variant__ on _some database backends_.


##### Multiple Table Deletes

Like `Update`, `Delete` supports the use of __correlated subqueries__ in the `WHERE` clause as well as _backend-specific_ __multiple table syntaxes__, such as `DELETE FROM...USING` on `MySQL`.


#### Getting Affected Row Count from UPDATE, DELETE

Both `Update` and `Delete` _support_ the ability to __return the number of rows matched__ after the statement proceeds, for _statements_ that are _invoked using Core_ `Connection`, i.e. `Connection.execute()` and this value is available from the `CursorResult.rowcount` attribute.

> ##### Tips
>
> The `CursorResult` class is a _subclass of Result_ which _contains additional attributes_ that are specific to the `DBAPI cursor object`. _An instance of this subclass is returned_ when a statement is _invoked_ via the `Connection.execute()` method. When using the `ORM`, the `Session.execute()` method returns an object of this type for all `INSERT`, `UPDATE`, and `DELETE` statements.

Facts about `CursorResult.rowcount`:

* The _value returned_ is the __number of rows matched__ by the `WHERE` clause of the statement. It __does not matter__ _if the row were_ __actually modified or not__.

* `CursorResult.rowcount` is __not necessarily available__ for an `UPDATE` or `DELETE` statement that uses `RETURNING`.

* For an `executemany` execution, `CursorResult.rowcount` __may not be available__ either, which _depends highly on the DBAPI module_ in use as well as _configured options_. The attribute `CursorResult.supports_sane_multi_rowcount` _indicates if this value_ will be __available__ _for the current backend_ in use.

* _Some drivers_, particularly _third party dialects_ for __`non-relational databases`, may not support__ `CursorResult.rowcount` at all. The `CursorResult.supports_sane_rowcount` will indicate this.

* `"rowcount"` is used by the `ORM` unit of work process to _validate_ that an `UPDATE` or `DELETE` statement __matched the expected number of rows__, and is also _essential_ for the __ORM versioning feature__ documented at `Configuring a Version Counter`.


#### Using RETURNING with UPDATE, DELETE

Like the `Insert` construct, `Update` and `Delete` __also support__ the `RETURNING` clause which is added by using the `Update.returning()` and `Delete.returning()` methods. When these methods are __used on a backend that supports RETURNING__, _selected columns from all rows that match the_ **`WHERE`** _criteria_ of the statement will be returned in the `Result` object as __rows that can be iterated__.
