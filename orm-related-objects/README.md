## Working with Related Objects

In this section, we will cover one more _essential ORM concept_, which is __how the ORM interacts with mapped classes that refer to other objects__. In the section `Declaring Mapped Classes`, the _mapped class_ examples made use of a construct called `relationship()`. This construct __defines a linkage__ between _two different mapped classes_, or from a _mapped class to itself_, the _latter_ of which is called a __`self-referential relationship`__. To describe the _basic idea_ of `relationship()`, first we'll review the mapping in short form, omitting the _Column mappings_ and other directives.

Above, the `User` class now has an _attribute_ `User.addresses` and the `Address` class has an _attribute_ `Address.user`. The `relationship()` construct will be used to __inspect the table relationships__ between the `Table` objects that are __mapped__ to the `User` and `Address` classes. As the `Table` object representing the _address table_ has a `ForeignKeyConstraint` which refers to the *user_account table*, the `relationship()` can _determine_ __unambiguously__ that there is a __one to many relationship__ _from_ `User.addresses` _to_ `User`; _one particular row_ in the `user_account` table __may be referred towards__ by _many rows_ in the `address` table.

_All one-to-many relationships_ __naturally correspond__ to a _many to one relationship_ in the _other direction_, in this case the one noted by `Address.user`. The `relationship.back_populates` parameter, seen above configured on both `relationship()` objects __referring__ to the _other name_, establishes that each of these two `relationship()` constructs should be __considered to be complimentary__ to _each other_; we will see how this plays out in the next section.


#### Persisting and Loading Relationships

We can start by _illustrating_ what `relationship()` does to instances of objects. If we make a new `User` object, we can note that there is a _Python list_ when we access the `.addresses` element.

This object is a _SQLAlchemy-specific version_ of _Python list_ which has the __ability to track and respond to changes__ made to it. The _collection_ also appeared __automatically__ when we _accessed the attribute_, even though we __never assigned__ it to the object. This is similar to the behavior noted at `Inserting Rows with the ORM` where it was observed that _column-based attributes_ to which we _don't explicitly assign a value_ also display as `None` __automatically__, rather than raising an `AttributeError` as would be Python's usual behavior.

As the `u1` object is still __transient__ and the _list_ that we got from `u1.addresses` has __not been mutated__ (i.e. _appended or extended_), it's __not actually `associated` with the object__ yet, but as we _make changes_ to it, it will become _part of the state_ of the `User` object.

The _collection_ is specific to the `Address` class which is the _only type of Python object_ that may be __persisted within it__. Using the `list.append()` method we may __add an Address object__. At this point, the `u1.addresses` _collection_ as expected _contains_ the __new `Address` object__.

As we _associated_ the `Address` object with the `User.addresses` _collection_ of the `u1` instance, another behavior also occurred, which is that the `User.addresses` _relationship_ __synchronized itself__ with the `Address.user` _relationship_, such that we __can navigate__ not only from the _User object to the Address object_, we __can also navigate__ from the _Address object back to the "parent" User object_.

This _synchronization_ occurred as a result of our _use of the_ `relationship.back_populates` parameter between the two `relationship()` objects. This parameter __names__ _another_ `relationship()` for which _complementary attribute_ __assignment/list mutation__ should occur. It will __work equally well__ in the _other direction_, which is that if we _create another_ `Address` _object_ and assign to its `Address.user` attribute, that `Address` becomes part of the `User.addresses` _collection_ on that `User` object.

We actually made use of the `user` parameter as a _keyword argument_ in the `Address` constructor, which is __accepted just like any other mapped attribute__ that was _declared_ on the `Address` class. It is __equivalent__ to _assignment_ of the `Address.user` attribute after the fact.


##### Cascading Objects into the Session

We now have a `User` and two `Address` objects that are _associated_ in a __bidirectional__ structure __in memory__, but as noted previously in `Inserting Rows with the ORM`, these objects are said to be in the __`transient state`__ until they are _associated_ with a `Session` object.

We make use of the `Session` that's __still ongoing__, and note that when we apply the `Session.add()` method to the lead `User` object, the _related_ `Address` object __also gets added__ to that _same_ `Session`.

The above behavior, where the `Session` _received_ a `User` object, and followed along the `User.addresses` _relationship_ to _locate a related_ `Address` object, is known as the __`save-update cascade`__.

The _three objects_ are now in the __pending state__; this means they are __ready__ to be the _subject_ of an `INSERT` operation but this has __not yet proceeded__; all _three objects_ have __no `primary key` assigned__ yet, and in addition, the `a1` and `a2` objects have an _attribute_ called `user_id` which refers to the `Column` that has a `ForeignKeyConstraint` referring to the `user_account.id` column; these are also `None` as the _objects_ are __not yet associated__ with a real database row.

It's at this _stage_ that we can see the very _great utility_ that the `unit of work process` provides; recall in the section `INSERT` usually _generates_ the `"values"` clause __automatically__, rows were inserted into the `user_account` and `address` tables using _some elaborate syntaxes_ in order to __automatically associate__ the `address.user_id` columns with those of the `user_account` rows. Additionally, it was __necessary__ that we __emit__ `INSERT` for `user_account` rows __first__, _before those of_ `address`, since rows in `address` are __dependent__ on their _parent row_ in `user_account` for a value in their `user_id` column.

When using the `Session`, all this _tedium_ is handled for us and even the most _die-hard_ SQL purist can __benefit from automation__ of `INSERT`, `UPDATE` and `DELETE` statements. When we `Session.commit()` the transaction _all steps invoke_ in the __correct order__, and furthermore the __newly generated `primary key`__ of the `user_account` row is applied to the `address.user_id` column _appropriately_.


#### Loading Relationships

In the last step, we called `Session.commit()` which emitted a `COMMIT` for the _transaction_, and then per `Session.commit.expire_on_commit` _expired all objects_ so that they __refresh__ for the _next transaction_.

When we __next__ _access an attribute_ on these objects, we'll see the `SELECT` __emitted__ for the _primary attributes_ of the row, such as when we view the __newly generated `primary key`__ for the `u1` object.

The _u1_ `User` object now has a _persistent collection_ `User.addresses` that we may also access. As this _collection_ consists of an _additional set of rows_ from the `address` table, when we _access this collection_ as well we again see a __lazy load emitted__ in order to __retrieve the objects__.

_Collections_ and _related attributes_ in the SQLAlchemy ORM are __persistent in memory__; once the _collection_ or _attribute_ is `populated`, _SQL_ is __no longer emitted__ until that _collection_ or _attribute_ is `expired`. We __may access__ `u1.addresses` again as well as _add_ or _remove_ items and this __will not incur__ any new SQL calls.

While the loading _emitted_ by __`lazy loading`__ can _quickly become expensive_ if we __don't take explicit steps__ to _optimize_ it, the _network of lazy loading_ at least is __fairly well optimized__ to __not perform redundant work__; as the `u1.addresses` collection was __refreshed__, per the _identity map_ these are in fact the __same `Address` instances__ as the `a1` and `a2` objects we've been dealing with already, so we're _done loading all attributes_ in this particular __object graph__.

The issue of how `relationships` load, or not, is an entire subject onto itself. Some additional introduction to these concepts is later in this section at `Loader Strategies`.


#### Using Relationships in Queries

The previous section introduced the _behavior_ of the `relationship()` construct when working with _instances of a mapped class_, above, the `u1`, `a1` and `a2` instances of the `User` and `Address` classes. In this section, we introduce the _behavior_ of `relationship()` as it applies to _class level behavior of a mapped class_, where it _serves_ in several ways to help __automate the construction of SQL queries__.


##### Using Relationships to Join

The sections `Explicit FROM clauses and JOINs` and `Setting the ON Clause` introduced the usage of the `Select.join()` and `Select.join_from()` methods to __compose__ _SQL JOIN clauses_. In order to describe __how to join between tables__, these methods either __infer__ the `ON clause` based on the presence of a _single unambiguous_ `ForeignKeyConstraint` object within the _table metadata structure_ that links the two tables, or otherwise we may _provide_ an __explicit__ `SQL Expression construct` that __indicates a specific ON clause__.

When _using ORM entities_, an _additional mechanism_ is available to help us set up the `ON clause` of a _join_, which is to make use of the `relationship()` objects that we set up in our user _mapping_, as was demonstrated at `Declaring Mapped Classes`. The _class-bound attribute_ corresponding to the `relationship()` may be passed as the __single argument__ to `Select.join()`, where it serves to __indicate both the `right side of the join` as well as the `ON clause` `at once`__.

The presence of an ORM `relationship()` on a _mapping_ is __not used__ by `Select.join()` or `Select.join_from()` _if we don't specify it_; it is __not used__ for `ON clause` _inference_. This means, if we _join from User to Address without an ON clause_, it __works__ because of the `ForeignKeyConstraint` _between the two mapped_ `Table` _objects_, __not because__ of the `relationship()` objects on the `User` and `Address` classes.


##### Joining between Aliased targets

In the section `ORM Entity Aliases` we introduced the `aliased()` construct, which is used to apply a _SQL alias_ to an _ORM entity_. When using a `relationship()` to help _construct SQL JOIN_, the use case where the _target of the join_ is to be an `aliased()` is suited by making use of the `PropComparator.of_type()` modifier. To demonstrate we will construct the same join illustrated at `ORM Entity Aliases` using the `relationship()` attributes to join instead.

To make use of a `relationship()` to _construct a join_ from an __aliased entity__, the _attribute_ is __available__ from the `aliased()` construct directly.


##### Augmenting the ON Criteria

The `ON clause` generated by the `relationship()` construct may also be __augmented with additional criteria__. This is __useful__ both for _quick ways to limit the scope of a particular join over a relationship path_, and also for use cases like _configuring loader strategies_, introduced below at `Loader Strategies`. The `PropComparator.and_()` method accepts a _series of SQL expressions_ __positionally__ that will be joined to the `ON clause` of the _JOIN_ __via `AND`__.


##### EXISTS forms: has()/any()

In the section `EXISTS subqueries`, we introduced the `Exists` object that provides for the _SQL EXISTS keyword_ in _conjunction_ with a `scalar subquery`. The `relationship()` construct provides for some _helper methods_ that may be used to __generate some common EXISTS styles of queries in terms of the relationship__.

For a __one-to-many relationship__ such as `User.addresses`, an `EXISTS` against the `address` table that __correlates back__ to the `user_account` table can be produced using `PropComparator.any()`. This method _accepts_ an __optional `WHERE` criteria__ to __limit the rows matched by the subquery__.

As `EXISTS` tends to be _more efficient_ __for `negative lookups`__, a _common query_ is to _locate entities_ where there are __no related entities present__. This is __succinct__ using a phrase such as `~User.addresses.any()`, to select for `User` entities that have __no related `Address` rows__.

The `PropComparator.has()` method works in mostly the same way as `PropComparator.any()`, _except_ that it's __used for `many-to-one` relationships__, such as if we wanted to __locate all `Address` objects which belonged to `"pearl"`__.


##### Common Relationship Operators

There are some _additional varieties_ of __SQL generation helpers__ that come with `relationship()`, including:

* __many to one equals comparison__ - a specific _object instance_ can be compared to __many-to-one relationship__, to select rows where the `foreign key` of the _target entity_ __matches__ the _primary key_ value of the _object_ given.

* __many to one not equals comparison__ - the _not equals operator_ may also be used.

* __object is contained in a one-to-many collection__ - this is _essentially_ the __one-to-many version__ of the `"equals" comparison`, select rows where the _primary key_ __equals__ the value of the _foreign key_ in a _related object_.

* __An object has a particular parent from a one-to-many perspective__ - the `with_parent()` function __produces a comparison__ that _returns rows_ which are __referred towards__ by a _given parent_, this is _essentially_ the __same as__ using the `"==" operator` with the __`"many-to-one"`__ side.


#### Loader Strategies

In the section `Loading Relationships` we introduced the concept that when we work with _instances of mapped objects_, _accessing the attributes_ that are mapped using `relationship()` in the _default case_ will __emit a lazy load__ when the _collection_ is __not populated__ in order to `load the objects` that _should be present_ in this _collection_.

`Lazy loading` is one of the __most famous__ _ORM patterns_, and is also the one that is __most controversial__. When _several dozen ORM objects in memory_ each refer to a _handful of unloaded attributes_, `routine manipulation` of these objects can __spin off many additional queries__ that __`can add up`__ (otherwise known as the __`N plus one problem`__), and to make matters __`worse`__ they are __emitted implicitly__. These _implicit queries_ `may not be noticed`, may __cause errors__ when they are _attempted_ __after__ there's _no longer a database transaction available_, or when using __alternative concurrency patterns__ such as `asyncio`, they actually __won't work__ at all.

At the same time, _lazy loading_ is a __vastly `popular` and `useful` pattern__ when it is _compatible_ with the __concurrency approach__ in use and __isn't otherwise causing problems__. For these reasons, SQLAlchemy's ORM places a _lot of emphasis_ on being able to `control` and `optimize` this _loading behavior_.

Above all, the __first step__ in _using ORM lazy loading_ __`effectively`__ is to `test the application`, `turn on SQL echoing`, and `watch the SQL` that is __emitted__. If there seem to be _lots of redundant_ `SELECT statements` that _look very much like_ they could be __`rolled into one` much more efficiently__, if there are `loads` __occurring inappropriately__ for objects that have been __detached__ from their `Session`, that's when to _look into using_ __`loader strategies`__.

_Loader strategies_ are represented as objects that __may be associated__ with a `SELECT statement` using the `Select.options()` method. They may be also __configured__ as _defaults_ for a `relationship()` using the `relationship.lazy` option.

Each _loader strategy_ object __adds some kind of information to the statement__ that will be __used later__ by the `Session` when it is _deciding how various attributes should be loaded and/or behave_ when they are accessed.


##### Selectin Load

The __most useful loader__ in modern SQLAlchemy is the `selectinload()` _loader option_. This option _solves the most common form_ of the __`"N plus one"`__ problem which is that of a _set of objects_ that __refer to related collections__. `selectinload()` will _ensure_ that _a particular collection_ for a full series of objects are __loaded up front using a single query__. It does this using a `SELECT` form that in most cases can be __emitted__ _against the related table alone_, __without the introduction__ of `JOIN`s or `subqueries`, and __only queries__ for those _parent objects_ for which the __collection isn't already loaded__. Below we illustrate `selectinload()` by _loading all_ of the __`User` objects__ and _all_ of their __related `Address` objects__; while we invoke `Session.execute()` __only once__, given a `select()` construct, when the database is accessed, there are in fact _two_ `SELECT` statements __emitted__, the _second_ one being to _fetch_ the __related `Address` objects__.


##### Joined Load

The `joinedload()` _eager load strategy_ is the __oldest__ _eager loader_ in SQLAlchemy, which __augments__ the `SELECT` statement that's being _passed to the database_ with a `JOIN` (which _may be an outer or an inner join_ depending on options), which can then __load in related objects__.

The `joinedload()` strategy is _best suited_ towards __loading related `many-to-one` objects__, as this __`only requires`__ that _additional columns_ are __added to a primary entity row__ that would be __fetched in any case__. For _greater efficiency_, it also accepts an option `joinedload.innerjoin` so that an __`inner join` instead of an `outer join`__ may be used for a case such as below where we know that all `Address` objects have an _associated_ `User`.

`joinedload()` also __works for collections__, meaning __`one-to-many`__ _relationships_, however it has the _effect of multiplying out primary rows per related item in a recursive way_ that __grows the amount of data__ sent for a result set by _orders of magnitude_ for _nested collections_ and/or _larger collections_, so _its use vs. another option_ such as `selectinload()` should be __evaluated on a per-case basis__.

It's _important_ to note that the `WHERE` and `ORDER BY` criteria of the _enclosing_ `Select` statement __do not target the table rendered by `joinedload()`__. Above, it can be seen in the SQL that an __anonymous alias__ is applied to the `user_account` table such that is __not directly addressable__ in the query. This concept is discussed in more detail in the section `The Zen of Joined Eager Loading`.

The `ON clause` rendered by `joinedload()` __may be affected directly__ by using the `PropComparator.and_()` method described previously at `Augmenting the ON Criteria`; examples of this technique with _loader strategies_ are further below at `Augmenting Loader Strategy Paths`. However, more generally, `"joined eager loading"` may be applied to a `Select` that uses `Select.join()` using the approach described in the next section, `Explicit Join + Eager load`.

> ##### Tip
> 
> It's important to note that _many-to-one_`eager loads` are __often not necessary__, as the __`"N plus one"`__ problem is _much less prevalent_ in the common case. When _many objects_ all __refer to the same related object__, such as _many_ `Address` objects that each refer to the _same_ `User`, `SQL` will be __emitted only once__ for that `User` object using _normal lazy loading_. The `lazy load routine` will _look up the related object_ __by primary key__ in the _current_ `Session` __without emitting any SQL when possible__.


##### Explicit Join + Eager load

If we were to _load_ `Address` rows while _joining_ to the `user_account` table using a method such as `Select.join()` to __render the `JOIN`__, we _could also leverage_ that `JOIN` in order to __eagerly load__ the contents of the `Address.user` _attribute_ on each `Address` object returned. This is _essentially_ that we are using __`"joined eager loading"`__ but __rendering the `JOIN` ourselves__. This common use case is achieved by using the `contains_eager()` option. This option is __very similar__ to `joinedload()`, except that it _assumes_ we have __set up the `JOIN` ourselves__, and it instead _only indicates_ that _additional columns_ in the `COLUMNS` clause __should be loaded into related attributes__ on _each_ returned object.

Above, we __both__ _filtered the rows_ on `user_account.name` and also __loaded rows__ from `user_account` into the `Address.user` attribute of the returned rows. If we had __applied `joinedload()` separately__, we would get a SQL query that __unnecessarily__ _joins twice_.


##### Augmenting Loader Strategy Paths

In `Augmenting the ON Criteria` we illustrated __how to add arbitrary criteria__ to a `JOIN` _rendered with_ `relationship()` to also _include additional criteria_ in the `ON clause`. The `PropComparator.and_()` method is in fact __generally available__ for _most loader options_. For example, if we wanted to __re-load__ the _names of users_ and _their email addresses_, but __omitting__ the _email addresses_ with the `sqlalchemy.org` domain, we can apply `PropComparator.and_()` to the argument passed to `selectinload()` to _limit_ this criteria.

A __very important__ thing to note above is that a `special option` is added with `.execution_options(populate_existing=True)`. This option which _takes effect when_ `rows` are _being fetched_ __indicates__ that the `loader option` we are using __should `replace` the `existing contents` of `collections` on the objects__, _if_ they are _already loaded_. As we are working with a _single_ `Session` __repeatedly__, the _objects_ we see __being loaded__ above are the __same `Python` instances__ as those that were _first persisted_ at the start of the ORM section of this notebook.


##### Raiseload

One additional _loader strategy_ worth mentioning is `raiseload()`. This option is used to __completely block an application__ from having the `"N plus one"` problem __at all__ by causing what would _normally_ be a `lazy load` to __raise an error instead__. It has _two variants_ that are _controlled_ via the `raiseload.sql_only` option _to block_ either __lazy loads that require SQL__, versus __all `"load"` operations__ including those which __only__ need to __consult the current `Session`__.

One way to use `raiseload()` is to _configure_ it on `relationship()` __itself__, by _setting_ `relationship.lazy` to the value `"raise_on_sql"`, so that for a particular _mapping_, a _certain relationship_ will __never try to emit SQL__.

Using such a _mapping_, the `application` is __blocked from `lazy loading`__, indicating that a particular query would __need to specify a loader strategy__.

The `exception` would _indicate_ that this collection should be __loaded up front instead__.

The `lazy="raise_on_sql"` option __tries to be smart__ about `many-to-one relationships` as well; above, if the `Address.user` attribute of an `Address` object were _not loaded_, but that `User` object _were locally present_ in the __same `Session`__, the `"raiseload"` strategy __would not raise an error__.
