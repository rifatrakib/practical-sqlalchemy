## Configuring a Version Counter

The _Mapper_ supports __management of a version id column__, which is a _single table column_ that __increments or otherwise updates__ its value _each time_ an `UPDATE` to the mapped table occurs. This value is checked each time the ORM emits an `UPDATE` or `DELETE` against the row to ensure that the value held in memory matches the database value.

> ##### Warning
>
> Because the _versioning feature_ relies upon comparison of the in memory record of an object, the feature __only applies__ to the `Session.flush()` process, where the ORM _flushes individual in-memory rows_ to the database. It __does not take effect__ when performing a __multirow UPDATE or DELETE__ using `Query.update()` or `Query.delete()` methods, as these methods __only emit__ an _UPDATE_ or _DELETE_ statement but otherwise __do not have direct access to the contents of those rows being affected__.

The _purpose_ of this feature is to __detect when two concurrent transactions are modifying the same row__ at roughly the same time, or alternatively to __provide a guard against the usage of a `"stale"` row__ in a system that might be re-using data from a previous transaction without refreshing (e.g. if one sets `expire_on_commit=False` with a _Session_, it is _possible to re-use the data from a previous transaction_).

> ##### Concurrent transaction updates
>
> When _detecting concurrent updates within transactions_, it is typically the case that the _database_'s `transaction isolation level` is _below_ the _level of repeatable read_; otherwise, the _transaction_ will __not be exposed__ to a _new row value_ created by a _concurrent update_ which __conflicts with the locally updated value__. In this case, the SQLAlchemy _versioning feature_ will typically __not be useful__ for _in-transaction conflict detection_, though it still __can be used__ for _cross-transaction staleness detection_.
>
> The database that _enforces repeatable reads_ will typically either have __locked the target row__ against a concurrent update, or is employing some form of _multi version concurrency control_ such that it will __emit an error__ when the transaction is committed. SQLAlchemy's `version_id_col` is an _alternative_ which __allows version tracking to occur for specific tables within a transaction__ that otherwise _might not have this isolation level set_.
