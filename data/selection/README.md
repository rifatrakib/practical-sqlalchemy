## Selecting Rows with Core or ORM

For both Core and ORM, the `select()` function generates a `Select construct` which is used for all `SELECT` queries. Passed to methods like _`Connection.execute()` in Core_ and _`Session.execute()` in ORM_, a `SELECT statement` is emitted in the _current transaction_ and the result rows available via the returned `Result` object.


#### The `select()` SQL Expression Construct

The `select()` construct builds up a statement in the same way as that of `insert()`, using a _generative approach_ where each method builds more state onto the object. Like the other SQL constructs, it can be _stringified_ in place.

Also in the same manner as all other statement-level `SQL constructs`, _to actually run the statement_ we pass it to an `execution` method. Since a `SELECT statement` returns _rows_ we can always iterate the result object to get _Row_ objects back.

When using the ORM, particularly with a `select()` construct that's _composed against ORM entities_, we will want to execute it using the `Session.execute()` method on the `Session`; using this approach, we continue to get `Row` objects from the result, however these rows are now _capable of including **complete entities**_, such as instances of the `User` class, as individual elements within each row.

While the SQL generated in these examples looks the same whether we invoke `select(user_table)` or `select(User)`, in the more general case they _do not necessarily render the same thing_, as an ORM-mapped class may be mapped to other kinds of `"selectables"` besides tables. __The `select()` that's against an ORM entity also indicates that ORM-mapped instances should be returned in a result, which is not the case when SELECTing from a Table object.__


#### Setting the COLUMNS and FROM clause

The `select()` function accepts positional elements representing any number of `Column` and/or `Table` expressions, as well as a _wide range of compatible objects_, which are resolved into a __list of SQL expressions__ to be `SELECT`ed from that will be returned as columns in the result set. These elements also serve in simpler cases to create the `FROM` clause, which is inferred from the _columns and table-like expressions_ passed.

To `SELECT` from individual columns using a Core approach, `Column` objects are accessed from the _`Table.c` accessor_ and __can be sent directly__; the `FROM` clause will be inferred as the set of all `Table` and other `FromClause` objects that are represented by those columns.

##### Selecting ORM Entities and Columns

_ORM entities_, such our `User class` as well as the _column-mapped attributes upon it_ such as `User.name`, also participate in the `SQL Expression Language system` representing __tables and columns__. Below illustrates an example of `SELECT`ing from the `User` entity, which ultimately renders in the same way as if we had used `user_table` directly.

When executing a statement like the above using the _ORM `Session.execute()` method_, there is __an important difference__ when we _select from a full entity such as `User`, as opposed to `user_table`_, which is that the `entity` itself is returned as _a single element_ within each row. That is, when we fetch rows from the above statement, as there is only the User entity in the list of things to fetch, we get back `Row` objects that have only one element, which contain _instances of the `User` class_.

A highly recommended convenience method of achieving the same result as above is to use the `Session.scalars()` method to _execute the statement **directly**_; this method will return a `ScalarResult` object that delivers the _first `column` of each row at once_, in this case, _instances of the `User` class_.

Alternatively, we can _select individual columns_ of an ORM entity as `distinct` elements within result rows, by _using the class-bound attributes_; when these are passed to a construct such as `select()`, they are resolved into the `Column` or other SQL expression represented by each attribute.

When we invoke this statement using `Session.execute()`, we now receive rows that have _individual elements per value_, each corresponding to a separate column or other SQL expression.

The approaches can also be mixed, as below where we `SELECT` the _name attribute_ of the User entity as the `first element of the row`, and **combine** it with _full Address entities_ in the `second element`.

Approaches towards _selecting ORM entities and columns_ as well as common methods for _converting rows_ are discussed further at `Selecting ORM Entities and Attributes`.


##### Selecting from Labeled SQL Expressions

The `ColumnElement.label()` method as well as the _same-named method_ available on `ORM attributes` provides a _SQL label of a column or expression_, allowing it to have a **specific name** in a result set. This can be helpful when _referring to arbitrary SQL expressions in a result row by name_.


##### Selecting with Textual Column Expressions

When we construct a `Select` object using the `select()` function, we are normally passing to it _a series of `Table` and `Column` objects_ that were defined using table metadata, or when using the ORM we may be sending `ORM-mapped attributes` that represent _table columns_. However, sometimes there is also the need to _manufacture arbitrary SQL blocks inside of statements_, such as `constant string expressions`, or just some arbitrary SQL that's quicker to write literally.

While the `text()` construct can be used in most places to _inject literal SQL phrases_, more often than not we are actually dealing with textual units that each represent an individual column expression. In this common case we can get more functionality out of our textual fragment using the `literal_column()` construct instead. This object is similar to `text()` except that _instead of representing arbitrary SQL of any form, it **explicitly represents `a single column`** and can then be `labeled and referred` towards in `subqueries and other expressions`_.

Note that _in both cases_, when using `text()` or `literal_column()`, we are writing a **syntactical SQL expression**, and _not a literal value_. We therefore have to include whatever quoting or syntaxes are necessary for the SQL we want to see rendered.


#### The WHERE clause

SQLAlchemy allows us to _compose SQL expressions_, such as `name = 'squidward'` or `user_id > 10`, by making use of _standard `Python operators` in conjunction with `Column` and similar objects_. For `boolean expressions`, most Python operators such as `==, !=, <, >= etc.` _generate new SQL Expression objects, rather than plain boolean `True/False` values_.

We can use expressions like these to _generate the `WHERE` clause_ by passing the resulting objects to the `Select.where()` method.

To produce _multiple expressions `joined by AND`_, the `Select.where()` method may be _invoked any number of times_.

A single call to `Select.where()` also _accepts multiple expressions_ with the same effect.

`AND` and `OR` conjunctions are both __available directly__ using the `and_()` and `or_()` functions, illustrated below in terms of _ORM entities_.

For *simple `"equality"` comparisons against a __single entity__*, there's also a popular method known as `Select.filter_by()` which accepts _keyword arguments that match to column keys or ORM attribute names_. It will filter against the _leftmost `FROM` clause_ or the _last entity joined_.


#### Explicit FROM clauses and JOINs

As mentioned previously, the `FROM` clause is usually _**inferred** based on the expressions_ that we are setting in the `columns` clause as well as other elements of the `Select`.

If we set a _single column_ from a particular `Table` in the `COLUMNS` clause, it puts that `Table` in the `FROM` clause as well.

If we were to put _columns from two tables_, then we get a `comma-separated FROM clause`.

In order to `JOIN` these two tables together, we typically use one of two methods on `Select`. The first is the `Select.join_from()` method, which _allows us to indicate the **left and right** side of the JOIN **explicitly**_.

The other is the the `Select.join()` method, which indicates only the **right side** of the `JOIN`, the _left hand-side is inferred_.

> ###### The ON Clause is inferred
>
> When using `Select.join_from()` or `Select.join()`, we may observe that the `ON clause` of the join is also __inferred__ for us in _simple foreign key cases_.

We also have the _option to add elements to the `FROM` clause explicitly_, if it is not inferred the way we want from the columns clause. We use the `Select.select_from()` method to achieve this, as below where we establish `user_table` as the first element in the FROM clause and `Select.join()` to establish `address_table` as the second.

Another example where we might want to use `Select.select_from()` is if our columns clause _doesn't have enough information_ to provide for a `FROM` clause. For example, to `SELECT` from the common SQL expression `count(*)`, we use a SQLAlchemy element known as `sqlalchemy.sql.expression.func` to produce the SQL `count()` function.


##### Setting the ON Clause

The previous examples of `JOIN` illustrated that the `Select` construct _can join between two tables and produce the ON clause automatically_. This occurs in those examples because _the `user_table` and `address_table` Table objects include **a single `ForeignKeyConstraint`** definition_ which is used to form this `ON` clause.

If the _`left and right targets of the join` do not have such a constraint_, or there are _multiple constraints_ in place, we __need to specify the `ON` clause directly__. Both `Select.join()` and `Select.join_from()` accept an additional argument for the `ON` clause, which is stated using the same SQL Expression mechanics as we saw about in The `WHERE` clause.

> **ORM Tip** - there's another way to generate the `ON` clause when _using ORM entities_ that make use of the `relationship()` construct, like the mapping set up in the previous section at `Declaring Mapped Classes`. This is a whole subject onto itself, which is introduced at length at Using Relationships to Join.


##### OUTER and FULL join

Both the `Select.join()` and `Select.join_from()` methods accept keyword arguments `Select.join.isouter` and `Select.join.full` which will render **`LEFT OUTER JOIN`** and **`FULL OUTER JOIN`**, respectively.

There is also a method `Select.outerjoin()` that is equivalent to using `.join(..., isouter=True)`.

> `SQL` also has a **`RIGHT OUTER JOIN`**. __`SQLAlchemy` doesn't render this directly__; instead, __reverse the order of the tables and use `LEFT OUTER JOIN`__.


#### ORDER BY, GROUP BY, HAVING

The `SELECT SQL statement` includes a clause called `ORDER BY` which is used to _return the selected rows within a given ordering_.

The `GROUP BY` clause is constructed similarly to the `ORDER BY` clause, and has the purpose of _sub-dividing the selected rows into specific groups upon which aggregate functions_ may be invoked. _The `HAVING` clause is usually used with `GROUP BY`_ and is of a similar form to the `WHERE` clause, except that it's _applied to the aggregated functions used within groups_.


#### ORDER BY

The `ORDER BY` clause is constructed in terms of SQL Expression constructs typically based on `Column` or _similar objects_. The `Select.order_by()` method accepts _one or more of these expressions_ **positionally**.

`Ascending/descending` is available from the `ColumnElement.asc()` and `ColumnElement.desc()` modifiers, which are present from _ORM-bound attributes_ as well.


#### Aggregate functions with `GROUP BY/HAVING`

In `SQL`, `aggregate functions` allow column expressions across multiple rows to be aggregated together to produce a single result. Examples include `counting`, `computing averages`, as well as locating the `maximum` or `minimum` value in a set of values.

SQLAlchemy provides for SQL functions in an _open-ended way_ using a namespace known as `func`. This is a _special constructor_ object which will _create new instances_ of `Function` when given the name of a particular SQL function, which can have _any name_, as well as _zero or more arguments_ to pass to the `function`, which are, like in all other cases, SQL Expression constructs. For example, to render the `SQL COUNT()` function against the `user_account.id` column, we call upon the `count()` name.

When using `aggregate functions` in `SQL`, the `GROUP BY` clause is __essential__ in that it `allows rows to be partitioned into groups` where _aggregate functions_ will be applied to each group __individually__. When requesting `non-aggregated columns` in the `COLUMNS` clause of a `SELECT` statement, SQL requires that these columns all be subject to a `GROUP BY` clause, either __directly or indirectly__ based on a `primary key association`. The `HAVING` clause is then used in a similar manner as the `WHERE` clause, except that it _filters out rows based on aggregated values_ rather than direct row contents. SQLAlchemy provides for these _two clauses_ using the `Select.group_by()` and `Select.having()` methods.


#### Ordering or Grouping by a Label

An important technique, in particular on some database backends, is the ability to `ORDER BY` or `GROUP BY` an expression that is already stated in the columns clause, __without re-stating__ the expression in the `ORDER BY` or `GROUP BY` clause and instead using the _column name_ or _labeled name_ from the `COLUMNS` clause. This form is available by passing the __string text of the name__ to the `Select.order_by()` or `Select.group_by()` method. The text passed is __not rendered directly__; instead, the name given to an expression in the columns clause and rendered as that expression name in context, raising an error if no match is found. The unary modifiers `asc()` and `desc()` may also be used in this form.


#### Using Aliases

Now that we are selecting from `multiple tables` and using __joins__, we quickly run into the case where we need to _refer to the same table `multiple` times_ in the `FROM` clause of a statement. We accomplish this using `SQL aliases`, which are a syntax that supplies an __alternative name__ to a `table or subquery` from which it can be referred towards in the statement.

In the SQLAlchemy Expression Language, these __names__ are instead represented by `FromClause` objects known as the __`Alias construct`__, which is constructed in `Core` using the `FromClause.alias()` method. An `Alias construct` is just like a `Table` construct in that it also has a _namespace of `Column` objects_ within the `Alias.c` collection.


#### ORM Entity Aliases

The ORM equivalent of the `FromClause.alias()` method is the ORM `aliased()` function, which may be applied to an entity such as `User` and `Address`. This produces a `Alias` object internally that's against the original mapped `Table` object, while maintaining ORM functionality.

As mentioned in `Setting` the `ON Clause`, the ORM provides for another way to join using the `relationship()` construct.


#### Subqueries and CTEs

A __`subquery`__ in SQL is a `SELECT` statement that is _rendered within parenthesis_ and _placed within the context of an enclosing statement_, _typically_ a `SELECT` statement but _not necessarily_.

This section will cover a so-called __non-scalar__ `subquery`, which is _typically placed in the FROM clause of an enclosing SELECT_. We will also cover the `Common Table Expression` or `CTE`, which is used in a similar way as a subquery, but includes _additional features_.

SQLAlchemy uses the `Subquery` object to represent a _subquery_ and the `CTE` to represent a _CTE_, usually obtained from the `Select.subquery()` and `Select.cte()` methods, respectively. Either object can be used as a `FROM` element `inside of a larger select()` construct.

We can construct a `Subquery` that will _select an aggregate count of rows_ from the address table (`aggregate functions` and `GROUP BY` were introduced previously at `Aggregate functions with GROUP BY/HAVING`).

The `Subquery` object behaves like any other `FROM` object such as a `Table`, notably that it includes a `Subquery.c` namespace of the columns which it selects. We can use this namespace to refer to both the `user_id` column as well as our custom labeled `count` expression.

With a selection of rows contained within the _subq_ object, we can _apply the object to a larger `Select`_ that will join the data to the `user_account` table.

In order to __join__ from `user_account` to `address`, we made use of the `Select.join_from()` method. As has been illustrated previously, the `ON clause` of this _join_ was again __inferred__ based on _foreign key constraints_. Even though a `SQL subquery` __does not itself have any constraints__, SQLAlchemy can act upon constraints represented on the columns by determining that the `subq.c.user_id` column is _derived from_ the `address_table.c.user_id` column, which __does express__ a `foreign key relationship` back to the `user_table.c.id` column which is then used to _generate_ the `ON clause`.


#### Common Table Expressions (CTEs)

Usage of the `CTE` construct in SQLAlchemy is _virtually the same_ as how the `Subquery` construct is used. By changing the invocation of the `Select.subquery()` method to use `Select.cte()` instead, we can use the resulting object as a `FROM` element in the same way, but the __SQL rendered is the very different__ common table expression syntax.

The `CTE` construct also features the ability to be used in a __recursive style__, and may in more elaborate cases be __composed from the RETURNING clause__ of an `INSERT, UPDATE or DELETE` statement. The docstring for `CTE` includes details on these additional patterns.

In both cases, the `subquery` and `CTE` were named at the SQL level using an __anonymous__ name. In the Python code, we don't need to provide these names at all. The __object identity__ of the `Subquery` or `CTE` instances serves as the __syntactical identity__ of the object when rendered. A _name that will be rendered_ in the SQL can be provided by passing it as the _first argument_ of the `Select.subquery()` or `Select.cte()` methods.


#### ORM Entity `Subqueries/CTEs`

In the ORM, the `aliased()` construct may be used to associate an ORM entity, such as our `User` or `Address` class, with any `FromClause` concept that represents a _source of rows_. The preceding section `ORM Entity Aliases` illustrates using `aliased()` to __associate the mapped class with an `Alias` of its mapped `Table`__. Here we illustrate `aliased()` doing the same thing against both a `Subquery` as well as a `CTE` generated against a `Select` construct, that ultimately derives from that same mapped `Table`.


#### Scalar and Correlated Subqueries

A `scalar subquery` is a _subquery_ that returns __exactly zero or one row and exactly one column__. The _subquery_ is then used in the `COLUMNS` or `WHERE` clause of an `enclosing SELECT statement` and is __different than a regular subquery__ in that it is __not used in the FROM clause__. A `correlated subquery` is a _scalar subquery_ that __refers to a table__ in the `enclosing SELECT statement`.

SQLAlchemy represents the _scalar subquery_ using the `ScalarSelect` construct, which is part of the __`ColumnElement` expression hierarchy__, in __contrast__ to the _regular subquery_ which is represented by the `Subquery` construct, which is in the `FromClause` hierarchy.

`Scalar subqueries` are __often, but not necessarily__, `used with aggregate functions`, introduced previously at `Aggregate functions with GROUP BY/HAVING`. A _scalar subquery_ is __indicated explicitly__ by making use of the `Select.scalar_subquery()` method as below. It's _default string form_ when `stringified` by itself _renders as an ordinary SELECT statement_ that is selecting from two tables.

The above `subq` object now __falls within__ the `ColumnElement` SQL expression hierarchy, in that it _may be used like any other column expression_.

Although the _scalar subquery_ by itself renders both `user_account` and `address` in its `FROM clause` when _stringified by itself_, when __embedding__ it into an `enclosing select() construct` that deals with the `user_account` table, the `user_account` table is __automatically correlated__, meaning it __does not render__ in the `FROM clause` of the subquery.

`Simple correlated subqueries` will usually __do the right thing__ that's desired. However, in the case where the _correlation is ambiguous_, SQLAlchemy will let us know that __`more clarity is needed`__.

To specify that the `user_table` is the one we seek to __correlate__ we specify this using the `ScalarSelect.correlate()` or `ScalarSelect.correlate_except()` methods. The statement then can return the data for this column like any other.


##### LATERAL correlation

`LATERAL correlation` is a _special sub-category of SQL correlation_ which __allows a selectable unit to refer to another selectable unit within a single `FROM clause`__. This is an `extremely special use case` which, while part of the SQL standard, is only known to be supported by __recent versions of PostgreSQL__.

Normally, if a `SELECT` statement refers to `table1 JOIN (SELECT ...) AS subquery` in its `FROM clause`, the `subquery on the right side` __may not refer to the `table1` expression from the left side__; `correlation` __may only refer to a table that is part of another SELECT that entirely encloses this SELECT__. The `LATERAL` keyword allows us to turn this behavior around and __allow correlation from the right side JOIN__.

SQLAlchemy supports this feature using the `Select.lateral()` method, which creates an object known as `Lateral`. `Lateral` is in the same family as `Subquery` and `Alias`, but also __includes correlation behavior__ when the construct is added to the `FROM clause` of an _enclosing SELECT_.

Above, the _right side_ of the `JOIN` is a `subquery` that __correlates__ to the `user_account` table that's on the _left side_ of the join.

When using `Select.lateral()`, the behavior of `Select.correlate()` and `Select.correlate_except()` methods is applied to the `Lateral` construct as well.


#### `UNION`, `UNION ALL` and other set operations

In SQL, `SELECT` statements __can be merged together__ using the `UNION` or `UNION ALL` SQL operation, which produces the _set of all rows produced by one or more statements together_. Other _set operations_ such as `INTERSECT [ALL]` and `EXCEPT [ALL]` are also possible.

SQLAlchemy's `Select` construct __supports compositions__ of this nature using functions like `union()`, `intersect()` and `except_()`, and the all counterparts `union_all()`, `intersect_all()` and `except_all()`. These functions all _accept an arbitrary number of sub-selectables_, which are typically `Select` constructs but _may also be an existing composition_.

The construct produced by these functions is the `CompoundSelect`, which is used in the same manner as the `Select` construct, except that it has __fewer methods__. The `CompoundSelect` produced by `union_all()` for example may be __invoked directly using Connection.execute()__.

To use a `CompoundSelect` as a _subquery_, just like `Select` it provides a `SelectBase.subquery()` method which will produce a `Subquery` object with a `FromClause.c collection` that __may be referred__ towards in an `enclosing select()`.


##### Selecting ORM Entities from Unions

The preceding examples illustrated how to construct a `UNION` given two `Table` objects, to then return database rows. If we wanted to use a `UNION` or _other set operation_ to select rows that we then receive as ORM objects, there are __two approaches__ that may be used. In both cases, we first construct a `select()` or `CompoundSelect` object that represents the `SELECT/UNION/etc statement` we want to execute; this statement should be _composed against the target ORM entities_ or their _underlying mapped Table objects_.

For a `simple SELECT with UNION` that is _not already nested inside of a subquery_, these can often be used in an _ORM object fetching context_ by using the `Select.from_statement()` method. With this approach, the `UNION` statement represents the entire query; __no additional criteria can be added after `Select.from_statement()` is used__.

To use a `UNION` or `other set-related construct` as an _entity-related component_ in in a more flexible manner, the `CompoundSelect` construct may be organized into a `subquery` using `CompoundSelect.subquery()`, which then __links to ORM objects using the aliased()__ function. This works in the same way introduced at `ORM Entity Subqueries/CTEs`, to first __create an ad-hoc `"mapping"`__ of our desired entity to the subquery, then selecting from that that new entity as though it were any other mapped class.


#### `EXISTS` subqueries

The SQL `EXISTS` keyword is an operator that is __used with scalar subqueries__ to _return a boolean true or false_ depending on if the `SELECT` statement would return a row. SQLAlchemy includes a variant of the `ScalarSelect` object called `Exists`, which will __generate an EXISTS subquery__ and is most conveniently generated using the `SelectBase.exists()` method.

The `EXISTS` construct is _more often_ than not __used as a negation__, e.g. `NOT EXISTS`, as it provides a _SQL-efficient form of locating rows_ for which a related table has no rows. Note the __binary negation operator (~)__ used inside the second `WHERE clause`.


#### Working with SQL Functions

First introduced earlier in this section at `Aggregate functions with GROUP BY/HAVING`, the `func` object serves as a __factory for creating new Function objects__, which when used in a construct like `select()`, _produce a SQL function display_, typically consisting of a `name`, `some parenthesis` (although __not always__), and possibly `some arguments`. Examples of _typical SQL functions_ include:

* the `count()` function, an _aggregate function_ which __counts how many rows__ are returned.

* the `lower()` function, a _string function_ that __converts a string to lower case__.

* the `now()` function, which provides for the __current date and time__; as this is a common function, `SQLAlchemy` _knows_ how to __render this differently for each backend__, in case of `SQLite` uses the `CURRENT_TIMESTAMP` function.

As _most database backends_ feature __dozens if not hundreds__ of `different SQL functions`, `func` tries to be __as liberal as possible__ in what it accepts. __Any name__ that is _accessed_ from this `namespace` is __automatically considered to be a SQL function__ that will _render in a generic way_.

At the same time, a _relatively small set of extremely common SQL functions_ such as `count`, `now`, `max`, `concat` include __pre-packaged versions__ of themselves which provide for __proper typing information__ as well as __backend-specific SQL generation__ in some cases.


##### Functions Have Return Types

As __functions are column expressions__, they also have `SQL datatypes` that _describe the data type of a generated SQL expression_. We refer to these types here as `"SQL return types"`, in reference to the type of `SQL value` that is returned by the function in the context of a _database-side SQL expression_, as opposed to the `"return type"` of a Python function.

The `SQL return type` of any SQL function _may be accessed, typically for debugging purposes_, by referring to the `Function.type` attribute.


These `SQL return types` are __significant__ when making use of the function expression in the context of a larger expression; that is, `math` operators will _work better_ when the `datatype of the expression` is something like __`Integer`__ or __`Numeric`__, _JSON accessors_ in order to work need to be using a type such as `JSON`. _Certain classes_ of functions __return entire rows__ instead of column values, where there is a _need to refer to specific columns_; such functions are referred towards as `table valued functions`.

The `SQL return type` of the function __may also be significant__ when _executing a statement and getting rows back_, for those cases where SQLAlchemy has to __apply result-set processing__. A prime example of this are _date-related functions on SQLite_, where SQLAlchemy's `DateTime and related datatypes` take on the role of __converting from string values to Python datetime() objects__ as result rows are received.

To __apply a `specific type` to a function__ we're creating, we pass it using the `Function.type_` parameter; the _type argument_ may be either a `TypeEngine class or an instance`. In the example below we pass the `JSON` class to generate the `PostgreSQL json_object()` function, noting that the _SQL return type will be of type JSON_.

##### Built-in Functions Have Pre-Configured Return Types

For _common aggregate functions_ like `count`, `max`, `min` as well as a very small number of _date functions_ like `now` and _string functions_ like `concat`, the `SQL return type` is __set up appropriately__, sometimes based on usage. The `max` function and _similar aggregate filtering functions_ will set up the `SQL return type` __based on the argument given__.

`Date and time functions` typically correspond to SQL expressions described by `DateTime`, `Date` or `Time`.

A _known string function_ such as `concat` will know that a SQL expression would be of type `String`.

However, for the _vast majority of SQL functions_, `SQLAlchemy` __does not have them explicitly present__ in its very small list of known functions. For example, while there is typically no issue using SQL functions `func.lower()` and `func.upper()` to __convert the casing of strings__, `SQLAlchemy` _doesn't actually know about these functions_, so they have a `"null"` SQL return type.

For _simple functions_ like `upper` and `lower`, the issue is __not usually significant__, as _string values may be received from the database without any special type handling_ on the SQLAlchemy side, and SQLAlchemy's `type coercion rules` can __often correctly guess__ intent as well; the Python `+` operator for example will be __correctly interpreted__ as the `string concatenation operator` based on looking at both sides of the expression.

Overall, the scenario where the `Function.type_` parameter __is likely necessary__ is:

1. the function is __not already a SQLAlchemy `built-in` function__; this can be _evidenced_ by `creating the function` and _observing the Function.type attribute_.

2. __`Function-aware` expression support is needed__; this most _typically_ refers to `special operators` _related to datatypes_ such as `JSON` or `ARRAY`.

3. __Result value processing is needed__, which may include types such as `DateTime`, `Boolean`, `Enum`, or again _special datatypes_ such as `JSON`, `ARRAY`.


##### Advanced SQL Function Techniques

The following subsections illustrate more things that can be done with `SQL functions`. While these techniques are `less common` and `more advanced` than basic SQL function use, they nonetheless are __extremely popular__, largely as a _result of PostgreSQL's emphasis on more complex function forms_, including `table- and column-valued forms` that are __popular with JSON data__.


##### Using Window Functions

A `window function` is a _special use_ of a `SQL aggregate function` which _calculates the aggregate value over the rows being returned in a group as the individual result rows are processed_. Whereas a function like `MAX()` will give you the _highest value of a column within a set of rows_, using the `same function as a "window function"` will given you the _highest value for each row, as of that row_.

In SQL, `window functions` allow one to __specify the rows over which the function should be applied__, a `"partition" value` which _considers the window over different sub-sets of rows_, and an `order by` expression which _importantly indicates the order in which rows should be applied to the aggregate function_.

In SQLAlchemy, __all SQL functions generated by the func namespace__ include a method `FunctionElement.over()` which __grants the window function, or `"OVER"`, syntax__; the construct produced is the `Over` construct.

A common function used with window functions is the `row_number()` function which simply __counts rows__. We may _partition_ this `row count` _against user name to number the email addresses of individual users_.

The `FunctionElement.over.partition_by` parameter is used so that the `PARTITION BY` clause is __rendered within the OVER clause__. We also may make use of the `ORDER BY` clause using `FunctionElement.over.order_by`.

> ##### Tip
>
> It's important to note that the `FunctionElement.over()` method __only applies__ to those SQL functions which are __in fact aggregate functions__; while the `Over` construct will _happily render itself for any SQL function_ given, the __database will reject the expression if the function itself is not a SQL aggregate function__.


##### Special Modifiers `WITHIN GROUP`, `FILTER`

The `"WITHIN GROUP"` SQL syntax is used in conjunction with an `"ordered set"` or a `"hypothetical set"` aggregate function. Common `"ordered set"` functions include `percentile_cont()` and `rank()`. SQLAlchemy includes __built-in implementations__ `rank`, `dense_rank`, `mode`, `percentile_cont` and `percentile_disc` which include a `FunctionElement.within_group()` method.

`"FILTER"` is _supported by some backends_ to __`limit the range of an aggregate function` to a particular subset of rows compared to the total range of rows returned__, available using the `FunctionElement.filter()` method.


##### Table-Valued Functions

`Table-valued SQL functions` support a __scalar representation that contains named sub-elements__. Often used for _JSON and ARRAY-oriented functions_ as well as functions like `generate_series()`, the _table-valued function_ is specified in the `FROM` clause, and is then __referred towards as a table, or sometimes even as a column__. Functions of this form are _prominent_ within the `PostgreSQL` database, however some forms of _table-valued functions_ are also supported by `SQLite`, `Oracle`, and `SQL Server`.

SQLAlchemy provides the `FunctionElement.table_valued()` method as the basic `"table-valued function"` construct, which will __convert a func object into a FROM clause containing a series of named columns__, _based on string names passed positionally_. This returns a `TableValuedAlias` object, which is a _function-enabled_ `Alias` construct that may be used as any other `FROM` clause as introduced at `Using Aliases`.


##### Column Valued Functions - Table Valued Function as a Scalar Column

_A special syntax supported by_ `PostgreSQL` and `Oracle` is that of __referring towards a function__ in the `FROM` clause, which then __delivers itself as a single column__ in the _columns clause_ of a `SELECT` statement or _other column expression context_. `PostgreSQL` makes great use of this syntax for such functions as `json_array_elements()`, `json_object_keys()`, `json_each_text()`, `json_each()`, etc. SQLAlchemy refers to this as a `"column valued" function` and is _available_ by applying the `FunctionElement.column_valued()` modifier to a `Function` construct.

The `"column valued"` form is _also supported_ by the `Oracle` dialect, where it is __usable for custom SQL functions__.


#### Data Casts and Type Coercion

In SQL, we often need to _indicate the datatype_ of an expression __explicitly__, either to tell the database _what type is expected_ in an otherwise ambiguous expression, or in some cases when we want to _convert the implied datatype_ of a SQL expression into something else. The SQL `CAST` keyword is used for this task, which in SQLAlchemy is provided by the `cast()` function. This function __accepts a column expression__ and a __data type object__ as arguments.

The `cast()` function not only __renders the SQL CAST syntax__, it also _produces a SQLAlchemy column expression_ that will __act as the given datatype on the Python side__ as well. A `string` expression that is `cast()` to `JSON` will gain __JSON subscript and comparison operators__.


##### `type_coerce()` - a Python-only `"cast"`

Sometimes there is the need to have SQLAlchemy know the datatype of an expression, for all the reasons mentioned above, but to _not render the `CAST` expression itself on the SQL side_, where it _may interfere with a SQL operation_ that already works without it. For this fairly common use case there is another function `type_coerce()` which is closely related to `cast()`, in that it __sets up a Python expression as having a specific SQL database type__, but __does not render__ the `CAST` keyword or datatype _on the database side_. `type_coerce()` is __particularly important__ when dealing with the `JSON` datatype, which typically has an __intricate relationship with string-oriented datatypes__ on different platforms and _may not even be an explicit datatype_, such as on `SQLite` and `MariaDB`. Below, we use `type_coerce()` to __deliver a Python structure__ as a `JSON string` into one of `MySQL`'s _JSON functions_.

`MySQL`'s `JSON_EXTRACT` _SQL function was invoked_ because we used `type_coerce()` to indicate that our __Python dictionary should be treated as JSON__. The Python `__getitem__` operator, `["some_key"]` in this case, __became available__ as a result and __allowed__ a `JSON_EXTRACT` _path expression_ (not shown, however in this case it would ultimately be `'$."some_key"'`) to be rendered.
