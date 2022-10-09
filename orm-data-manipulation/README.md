## Data Manipulation with the ORM

The previous section `Working with Data` remained focused on the _SQL Expression Language_ from a _Core perspective_, in order to __provide continuity__ across the _major SQL statement constructs_. This section will then build out the lifecycle of the `Session` and __how it interacts with these constructs__.

**Prerequisite Sections** - the ORM focused part builds upon two previous _ORM-centric sections_ in this document:

* __Executing with an ORM Session__ - introduces how to make an ORM `Session` object.

* __Defining Table Metadata with the ORM__ - where we set up our _ORM mappings_ of the `User` and `Address` entities.

* __Selecting ORM Entities and Columns__ - a few examples on _how to run SELECT statements_ for entities like `User`.


#### Inserting Rows with the ORM

When using the ORM, the `Session` object is responsible for __constructing Insert constructs__ and __emitting__ them for us in a _transaction_. The way we instruct the `Session` to do so is by __adding object entries__ to it; the `Session` then makes sure these _new entries_ will be _emitted to the database_ when they are needed, using a process known as a __`flush`__.


##### Instances of Classes represent Rows

Whereas in the previous example we __emitted an `INSERT`__ using Python dictionaries to indicate the _data we wanted to add_, with the ORM we make _direct use of the custom Python classes_ we defined, back at `Defining Table Metadata with the ORM`. At the _class level_, the `User` and `Address` classes served as a place to define what the __corresponding database tables__ should look like. These classes also serve as __extensible data objects__ that we use to _create and manipulate rows within a transaction_ as well.

We are able to construct these objects using the _names of the mapped columns as keyword arguments_ in the constructor. This is possible as the `User` class includes an __automatically generated__ `__init__()` constructor that was _provided by the ORM mapping_ so that we could create each object using _column names as keys in the constructor_.

In a similar manner as in our _Core examples_ of `Insert`, we __did not include a primary key__ (i.e. an entry for the `id` column), since we would like to make use of the _auto-incrementing primary key feature of the database_, `SQLite` in this case, which the ORM also integrates with. The value of the `id` attribute before inserting, if we were to view it, displays itself as `None`.

The `None` value is provided by `SQLAlchemy` to indicate that the __attribute has no value__ as of yet. _SQLAlchemy-mapped attributes_ always __return a value in Python__ and _don't raise AttributeError if they're missing_, when dealing with a new object that has not had a value assigned.

At the moment, the objects _before executing_ in a `session` are said to be in a _state_ called `transient` - they are __`not associated` with any database state__ and are __yet to be associated with a `Session` object__ that can _generate_ `INSERT` statements for them.


##### Adding objects to a Session

To illustrate the _addition_ process step by step, we will create a `Session` without using a _context manager_ (and hence we must make sure we close it later!).

The __objects are then added to the `Session`__ using the `Session.add()` method. When this is called, the objects are in a _state_ known as __`pending`__ and _have not been inserted_ yet.

When we have _pending objects_, we can see this _state_ by looking at a _collection_ on the `Session` called `Session.new`.

The above view is using a __collection__ called `IdentitySet` that is _essentially_ a `Python set` that __hashes on object identity__ in all cases (i.e., using Python built-in `id()` function, rather than the Python `hash()` function).


##### Flushing

The `Session` makes use of a _pattern_ known as __`unit of work`__. This generally means it __accumulates changes one at a time__, but _does not actually communicate them_ to the database __until needed__. This allows it to __make better decisions__ about _how SQL DML should be emitted_ in the `transaction` based on a given __set of `pending` changes__. When it does _emit SQL to the database to push out the current set of changes_, the process is known as a `flush`. We can illustrate the _flush process_ __manually__ by calling the `Session.flush()` method.

Above we observe the `Session` was _first called_ upon to __emit SQL__, so it _created a new transaction_ and __emitted__ the _appropriate INSERT statements_ for the two objects. The `transaction` now __remains open__ _until_ we call any of the `Session.commit()`, `Session.rollback()`, or `Session.close()` methods of `Session`.

While `Session.flush()` may be used to _manually_ __push out pending changes__ to the _current transaction_, it is _usually unnecessary_ as the `Session` features a behavior known as __`autoflush`__, which we will illustrate later. It also _flushes out changes_ whenever `Session.commit()` is called.


##### Autogenerated primary key attributes

Once the _rows_ are __inserted__, the two _Python objects_ we've created are in a _state_ known as __`persistent`__, where they are _associated_ with the `Session` object in which they were __added or loaded__, and _feature lots of other behaviors_ that will be covered later.

Another effect of the `INSERT` that occurred was that the __ORM has retrieved the `new primary key identifiers` for each new object__; _internally_ it normally uses the same `CursorResult.inserted_primary_key` accessor we introduced previously. The `squidward` and `krabs` objects now have these _new primary key identifiers_ __associated with them__ and we can view them by _acesssing_ the `id` attribute.

> ##### Tip
> 
> __Why did the ORM emit `two separate INSERT statements` when it could have used `executemany`?__
> As we'll see in the next section, the `Session` when __flushing objects__ always _needs to know the primary key of newly inserted objects_. If a feature such as _SQLite's autoincrement_ is used (other examples include __PostgreSQL__ `IDENTITY` or `SERIAL`, `using sequences`, etc.), the `CursorResult.inserted_primary_key` feature usually requires that __each `INSERT`__ is __emitted one row at a time__. If we had _provided values for the primary keys ahead of time_, the ORM would have been __able to optimize the operation better__. Some database backends such as `psycopg2` __can__ also `INSERT` _many rows at once_ while still being __able to retrieve the primary key values__.


##### Getting Objects by Primary Key from the Identity Map

The `primary key identity` of the objects are __significant__ to the `Session`, as the objects are now _linked to this identity in memory_ using a feature known as the `identity map`. The `identity map` is an __in-memory store__ that __links__ all objects _currently loaded_ __`in memory`__ to their `primary key identity`. We can observe this by _retrieving_ one of the above objects using the `Session.get()` method, which will _return an entry from the identity map_ __if locally present__, _otherwise_ __emitting a `SELECT`__.

The _important_ thing to note about the `identity map` is that it __maintains a unique instance__ of a _particular Python object per a particular database identity_, __within the scope__ of a particular `Session` object.

The `identity map` is a _critical feature_ that __allows complex sets of objects__ to be __manipulated__ _within a transaction without things getting out of sync_.


##### Committing

There's much more to say about how the `Session` works which will be discussed further. For now we will __commit the transaction__ so that we can build up knowledge on how to `SELECT` rows before examining more ORM behaviors and features.

The above operation will __commit the transaction__ that was _in progress_. The `objects` which we've dealt with are __still attached__ to the `Session`, which is a _state_ they stay in __until the `Session` is closed__ (which is introduced at `Closing a Session`).

> ##### Tips
> 
> An _important_ thing to note is that `attributes on the objects` that we just worked with have been __`expired`__, _meaning_, when we next _access any attributes_ on them, the `Session` will __start a new transaction and re-load their state__. This _option_ is __sometimes problematic__ for both _performance reasons_, or if one wishes to _use the objects after closing_ the __`Session`__ (which is known as the `detached state`), as they _will not have any state_ and _will have no_ `Session` with which _to load that state_, leading to __`"detached instance"` errors__. The behavior is __controllable__ using a parameter called `Session.expire_on_commit`. More on this is at `Closing a Session`.


#### Updating ORM Objects

In the preceding section `Updating and Deleting Rows with Core`, we introduced the `Update` construct that represents _SQL UPDATE statement_. When using the ORM, there are __two ways__ in which this construct is used. The _primary way_ is that it is __emitted automatically__ as part of the _unit of work process_ used by the `Session`, where an `UPDATE` statement is _emitted on a per-primary key basis corresponding to individual objects_ that have changes on them. A _second_ form of `UPDATE` is called an __`"ORM enabled UPDATE"`__ and allows us to use the `Update` construct with the `Session` __explicitly__; this is described in the next section.

Supposing we loaded the `User` object for the _username_ `sandy` into a _transaction_ (also showing off the `Select.filter_by()` method as well as the `Result.scalar_one()` method).

The _Python object_ `sandy` as mentioned before _acts as a_ __proxy__ for the _row in the database_, more specifically the _database row in terms of the_ __current transaction__, that has the primary key identity of 1.

If we __alter__ the _attributes_ of this object, the `Session` __tracks this change__. The _object_ __appears in a collection__ called `Session.dirty`, indicating the object is __`"dirty"`__.

When the `Session` _next_ __emits a flush__, an `UPDATE` will be _emitted_ that __updates__ this _value in the database_. As mentioned previously, a `flush` occurs __automatically__ _before we emit any SELECT_, using a behavior known as `autoflush`. We can __query directly__ for the `User.fullname` column from this row and we will get our _updated value back_.

We can see above that we requested that the `Session` __execute__ a _single_ `select()` statement. However the _SQL emitted_ shows that an `UPDATE were emitted as well`, which was the `flush process` __pushing out pending changes__. The `sandy` _Python object_ is now __no longer considered `dirty`__.

However note we are __still in a `transaction`__ and our _changes_ __have not been pushed__ to the _database's permanent storage_. Since _Sandy's last name_ is in fact `"Cheeks"` not `"Squirrel"`, we will __repair__ _this mistake_ later when we __roll back the transaction__. But first we'll make some more data changes.


##### ORM-enabled UPDATE statements

As previously mentioned, there's a _second way_ to __emit `UPDATE` statements__ in terms of the ORM, which is known as an __`ORM enabled UPDATE statement`__. This allows the use of a _generic SQL UPDATE statement_ that __can affect many rows at once__.

When _invoking_ the __ORM-enabled `UPDATE` statement__, _special logic_ is used to __locate__ objects in the `current session` that _match the given criteria_, so that they are __refreshed__ _with the new data_.

The _refresh logic_ is known as the `synchronize_session` option, and is described in detail in the section `UPDATE and DELETE with arbitrary WHERE clause`.


#### Deleting ORM Objects

To __round out__ the _basic persistence operations_, an _individual ORM object_ __may be marked for deletion__ by using the `Session.delete()` method. If we _mark an object_ for __deletion__, as is the case with other operations, _nothing actually happens yet until a flush proceeds_. Current ORM behavior is that `the object` __stays in the `Session` until the `flush` proceeds__, which as mentioned before _occurs if we emit a query_.

Above, the `SELECT` we asked to _emit_ was __preceded by a `DELETE`__, which indicated the __pending deletion__ for patrick __proceeded__. There was also a `SELECT` against the `address` table, which was _prompted_ by the ORM _looking for rows in this table which may be related to the target row_; this behavior is part of a behavior known as __cascade__, and __can be tailored__ to work __more efficiently__ by _allowing the database_ to _handle related rows_ in address _automatically_; the section delete has all the detail on this.

Beyond that, the object instance being _deleted_ is __no longer__ considered to be __persistent within the `Session`__, as can be shown by the _containment check_.

However just like the `UPDATE`s we made to the `sandy` object, _every change_ we've made here is __local to an ongoing transaction__, which __won't become `permanent` if we don't `commit` it__.


##### ORM-enabled DELETE Statements

Like `UPDATE` operations, there is also an _ORM-enabled version_ of `DELETE` which we can illustrate by using the `delete()` construct with `Session.execute()`. It also has a feature by which _non expired objects_ (see expired) that __match the given deletion criteria__ will be __automatically marked__ as `"deleted"` in the `Session`.

The __`squidward` identity__, like that of `patrick`, is now also __in a `deleted` state__. Note that we had to _re-load_ squidward above in order to demonstrate this; if the object were _expired_, the `DELETE` operation __would not take the time to refresh expired objects__ just to see that they had been deleted.


#### Rolling Back

The `Session` has a `Session.rollback()` method that as expected __emits a `ROLLBACK` on the SQL connection in progress__. However, it also has an effect on the _objects_ that are __currently associated__ with the `Session`, in our previous example the Python object `sandy`. While we changed the `.fullname` of the `sandy` object to read `"Sandy Squirrel"`, we want to __roll back__ this change. Calling `Session.rollback()` will not only __roll back the transaction__ but also __expire all objects currently associated__ with this `Session`, which will have the effect that they will __refresh themselves__ when _next accessed_ using a process known as __`lazy loading`__.

_To view_ the `"expiration"` process __more closely__, we may observe that the Python object `sandy` has __no state left__ within its Python `__dict__`, with the exception of a _special SQLAlchemy internal state object_.

This is the `"expired"` state; _accessing the attribute again_ will __autobegin__ a `new transaction` and `refresh` sandy with the __current database row__. We may now observe that the _full database row_ was also __populated__ into the `__dict__` of the sandy object.

For _deleted_ objects, when we earlier noted that `patrick` was __no longer in the session__, that _object's identity_ is also __restored__, and of course the _database data_ is __present__ again as well.


#### Closing a Session

Within the above sections we used a `Session` object __outside__ of a _Python context manager_, that is, we __didn't use__ the `with statement`. That's fine, however if we are doing things this way, it's best that we __explicitly__ `close` out the `Session` when we are done with it.

__Closing the `Session`__, which is what happens when we use it in a _context manager_ as well, accomplishes the following things:

* It __releases__ all _connection resources_ to the `connection pool`, _cancelling out_ (e.g. `rolling back`) _any transactions_ that were __in progress__.

This means that when we make use of a `session` to perform some __read-only__ tasks and then `close` it, we __don't need to explicitly call__ upon `Session.rollback()` to _make sure_ the _transaction is rolled back_; the `connection pool` handles this.

* It __expunges__ all objects from the `Session`.

This means that _all the Python objects_ we had __loaded__ for this `Session`, like _sandy, patrick and squidward_, are now in a `state` known as __detached__. In particular, we will note that _objects_ that were still in an __expired state__, for example due to the call to `Session.commit()`, are now __non-functional__, as they _don't contain the state of a current row_ and are _no longer associated with any database transaction_ in which to be refreshed.

The __detached__ objects __can be re-associated__ with the _same, or a new_ `Session` using the `Session.add()` method, which will __re-establish their relationship__ with their _particular database row_.

> ##### Tip
> 
> Try to _avoid using objects_ in their __detached__ state, if possible. When the `Session` is _closed_, __clean up references__ to all the _previously attached objects_ as well. For cases where __detached__ objects are _necessary_, typically the _immediate display_ of _just-committed objects_ for a _web application_ where the `Session` is __closed__ _before the view is rendered_, set the `Session.expire_on_commit` _flag_ to `False`.
