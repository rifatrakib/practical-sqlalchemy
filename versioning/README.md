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


#### Simple Version Counting

The most _straightforward_ way to __track versions__ is to _add an integer column_ to the mapped table, then establish it as the `version_id_col` within the mapper options.

```
class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    version_id = Column(Integer, nullable=False)
    name = Column(String(50), nullable=False)
    
    __mapper_args__ = {"version_id_col": version_id}
```

> ##### Note
>
> It is __strongly recommended__ that the `version_id` column be made _NOT NULL_. The _versioning feature_ __does not support a NULL value in the versioning column__.

Above, the _User_ mapping __tracks integer versions__ using the column `version_id`. When an object of type _User_ is _first flushed_, the `version_id` column will be given a value of `"1"`. Then, an _UPDATE_ of the table later on __will always be emitted__ in a manner similar to the following:

```
UPDATE user SET version_id=:version_id, name=:name
WHERE user.id = :user_id AND user.version_id = :user_version_id
{"name": "new name", "version_id": 2, "user_id": 1, "user_version_id": 1}
```

The above _UPDATE_ statement is updating the row that not only matches `user.id = 1`, it also is __requiring__ that `user.version_id = 1`, where `"1"` is the __last version identifier__ we've been known to use on this object. If a transaction elsewhere has modified the row independently, this _version id_ will no longer match, and the _UPDATE_ statement will __report that no rows matched__; this is the condition that SQLAlchemy tests, that __exactly one row matched our UPDATE (or DELETE) statement__. If _zero rows match_, that _indicates_ our version of the data is __stale__, and a `StaleDataError` is raised.


#### Custom Version Counters/Types

Other kinds of values or _counters_ can be used for _versioning_. Common types include `dates` and `GUIDs`. When using an _alternate type or counter scheme_, SQLAlchemy provides a _hook_ for this scheme using the `version_id_generator` argument, which _accepts_ a `version generation callable`. This callable is passed the value of the _current known version_, and is expected to __return the subsequent version__.

For example, if we wanted to _track the versioning_ of our _User_ class using a _randomly generated GUID_, we could do this (note that some backends support a native GUID type, but we illustrate here using a simple string).

```
class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    version_uuid = Column(String(32), nullable=False)
    name = Column(String(50), nullable=False)
    
    __mapper_args__ = {
        "version_id_col": version_uuid,
        "version_id_generator": lambda version: uuid.uuid4().hex,
    }
```

The _persistence engine_ will call upon `uuid.uuid4()` each time a _User_ object is __subject to an INSERT or an UPDATE__. In this case, our _version generation function_ can __disregard__ the _incoming value of version_, as the `uuid4()` function __generates identifiers without any prerequisite value__. If we were using a _sequential versioning scheme_ such as numeric or a special character system, we could make use of the given version in order to help determine the subsequent value.
