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


#### Server Side Version Counters

The `version_id_generator` can also be _configured to rely upon_ a value that is __generated by the database__. In this case, the database would need some means of __generating new identifiers__ when a row is _subject to an INSERT_ as well as with an _UPDATE_. For the _UPDATE_ case, typically an _update trigger_ is needed, unless the database in question supports some other __native version identifier__. The _PostgreSQL_ database in particular supports a _system column_ called `xmin` which __provides UPDATE versioning__. We can make use of the _PostgreSQL_ `xmin` column to version our _User_ class as follows.

```
class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    xmin = Column("xmin", String, system=True, server_default=FetchedValue())
    
    __mapper_args__ = {"version_id_col": xmin, "version_id_generator": False}
```

With the above mapping, the ORM will rely upon the _xmin_ column for __automatically__ providing the _new value of the version id counter_.

> ##### creating tables that refer to system columns
>
> In the above scenario, as _xmin_ is a __system column__ provided by PostgreSQL, we use the `system=True` argument to _mark it as a system-provided column_, __omitted from the `CREATE TABLE` statement__. The _datatype_ of this column is an _internal PostgreSQL type_ called `xid` which acts mostly __like a string__, so we use the `String` datatype.

The ORM typically __does not actively fetch__ the values of _database-generated_ values when it _emits_ an `INSERT` or `UPDATE`, instead leaving these columns as `"expired"` and to be fetched when they are _next accessed_, unless the __eager_defaults `mapper()` flag__ is set. However, when a _server side version column_ is used, the ORM __needs to actively fetch__ the _newly generated value_. This is so that the _version counter_ is __set up before any concurrent transaction may update it again__. This fetching is also __best done simultaneously within the `INSERT` or `UPDATE` statement using `RETURNING`__, otherwise if _emitting a SELECT statement afterwards_, there is still a __potential `race condition`__ where the _version counter_ __may change before it can be fetched__.

When the target database supports _RETURNING_, an _INSERT_ statement for our _User_ class will look like this:

```
INSERT INTO "user" (name) VALUES (%(name)s) RETURNING "user".id, "user".xmin
{'name': 'ed'}
```

Where above, the ORM __can acquire__ any _newly generated primary key values_ along with _server-generated version identifiers_ in one statement. When the __backend does not support `RETURNING`__, an __additional `SELECT` must be emitted__ for every _INSERT_ and _UPDATE_, which is __much less efficient__, and also introduces the _possibility of missed version counters_:

```
INSERT INTO "user" (name) VALUES (%(name)s)
{'name': 'ed'}

SELECT "user".version_id AS user_version_id FROM "user" where
"user".id = :param_1
{"param_1": 1}
```

It is __strongly recommended__ that _server side version counters_ only be used when __absolutely necessary__ and __only on backends that support `RETURNING`__, e.g. _PostgreSQL_, _Oracle_, _SQL Server_ (though SQL Server has major caveats when triggers are used), _Firebird_.
