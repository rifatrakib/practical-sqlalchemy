## SQL Expressions as Mapped Attributes

_Attributes_ on a mapped class __can be linked__ to `SQL expressions`, which can be used in queries.


#### Using a Hybrid

The _easiest_ and _most flexible_ way to __link relatively simple SQL expressions__ to a class is to use a so-called `"hybrid attribute"`, described in the section `Hybrid Attributes`. The _hybrid_ provides for an _expression_ that works at both the _Python level_ as well as at the _SQL expression level_. For example, below we map a class `User`, containing attributes _firstname_ and _lastname_, and _include a hybrid_ that will provide for us the _fullname_, which is the `string concatenation` of the two.

```
class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    
    @hybrid_property
    def fullname(self):
        return f"{self.firstname} {self.lastname}"
```

Above, the _fullname_ attribute is __interpreted at both the instance and class level__, so that it is available from an instance.

```
some_user = session.query(User).first()
print(some_user.fullname)
```

as well as usable within queries:

```
some_user = session.query(User).filter(User.fullname == "John Smith").first()
```

The _string concatenation_ example is a simple one, where the _Python expression_ __can be dual purposed__ at the _instance and class level_. Often, the _SQL expression_ __must be distinguished__ from the _Python expression_, which can be achieved using `hybrid_property.expression()`. Below we illustrate the case where a __conditional needs to be present inside the hybrid__, using the `if statement` in _Python_ and the `case()` construct for _SQL expressions_.


#### Using column_property

The `column_property()` function can be used to __map a SQL expression__ in a manner similar to a _regularly mapped_ `Column`. With this technique, the _attribute_ is __loaded along with all other column-mapped attributes at load time__. This is in some cases an _advantage_ over the usage of hybrids, as the value can be loaded up front at the same time as the parent row of the object, particularly if the expression is one which links to other tables (typically as a _correlated subquery_) to access data that wouldn't normally be available on an already loaded object.

_Disadvantages_ to using `column_property()` for SQL expressions include that the __expression must be compatible with the SELECT statement emitted__ for the class as a whole, and there are also _some configurational quirks_ which can occur when using `column_property()` from _declarative mixins_.

_Correlated subqueries_ may be used as well. Below we use the `select()` construct to create a `ScalarSelect`, representing a __column-oriented `SELECT` statement__, that _links together the count_ of `Address` objects available for a particular `User`.

In the above example, we define a `ScalarSelect()` construct like the following:

```
stmt = (
    select(func.count(Address.id))
    .where(Address.user_id == id)
    .correlate_except(Address)
    .scalar_subquery()
)
```

Above, we first use `select()` to create a `Select` construct, which we then __convert into a scalar subquery__ using the `Select.scalar_subquery()` method, indicating our intent to use this `Select` statement in a _column expression context_.

Within the `Select` itself, we select the _count_ of `Address.id` rows where the `Address.user_id` column is __equated to id__, which in the context of the `User` class is the `Column` named _id_ (note that _id_ is also the name of a Python built in function, which is not what we want to use here - if we were outside of the `User` class definition, we'd use User.id).

The `Select.correlate_except()` method indicates that each element in the `FROM` clause of this `select()` __may be omitted from the `FROM` list__ (that is, _correlated_ to the __enclosing `SELECT` statement__ against `User`) except for the one corresponding to `Address`. This __isn't strictly necessary__, but _prevents_ `Address` from __being inadvertently omitted__ from the `FROM` list in the case of a _long string of joins_ between `User` and `Address` tables where `SELECT` statements against `Address` are _nested_.

If import issues prevent the `column_property()` from being _defined inline_ with the class, it __can be assigned to the class after both are configured__. When _using mappings_ that make use of a `declarative_base()` base class, this _attribute assignment_ has the effect of calling `Mapper.add_property()` to add an additional property after the fact.

```
# only works if a declarative base class is in use
User.address_count = column_property(
    select(func.count(Address.id)).where(Address.user_id == User.id).scalar_subquery()
)
```

When using _mapping styles_ that __don't use__ `declarative_base()`, such as the `registry.mapped()` decorator, the `Mapper.add_property()` method __may be invoked explicitly__ on the underlying `Mapper` object, which can be obtained using `inspect()`.

For a `column_property()` that refers to columns linked from a _many-to-many relationship_, use `and_()` to __join the fields of the association table__ to both tables in a _relationship_.


##### Composing from Column Properties at Mapping Time

It is possible to create _mappings_ that __combine multiple `ColumnProperty` objects__ together. The `ColumnProperty` will be interpreted as a SQL expression when used in a _Core expression context_, provided that it is targeted by an existing expression object; this works by the _Core_ detecting that the object has a `__clause_element__()` method which returns a SQL expression. However, if the `ColumnProperty` is used as a _lead object_ in an expression where there is __no other Core SQL expression object to target it__, the `ColumnProperty.expression` attribute will __return the underlying SQL expression__ so that it can be used to _build SQL expressions consistently_. Below, the `File` class contains an attribute `File.path` that _concatenates a string token_ to the `File.filename` attribute, which is itself a `ColumnProperty`.

```
class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    extension = Column(String(8))
    filename = column_property(name + "." + extension)
    path = column_property("C:/" + filename.expression)
```

When the `File` class is used in expressions normally, the attributes assigned to _filename_ and _path_ are __usable directly__. The use of the `ColumnProperty.expression` attribute is __only necessary when using the `ColumnProperty` directly__ within the mapping definition.

```
q = session.query(File.path).filter(File.filename == "foo.txt")
```


#### Using a plain descriptor

In cases where an SQL query more elaborate than what `column_property()` or `hybrid_property` can provide must be emitted, a __regular Python function accessed as an attribute__ can be used, assuming the expression __only needs to be available__ on an _already-loaded instance_. The function is decorated with Python's own `@property` decorator __to mark it as a read-only attribute__. Within the function, `object_session()` is used to _locate_ the `Session` corresponding to the current object, which is then used to emit a query.

The _plain descriptor approach_ is useful as a __last resort__, but is __less performant__ in the usual case than _both the hybrid and column property approaches_, in that it needs to emit a SQL query upon each access.


#### Query-time SQL expressions as mapped attributes

When using `Session.query()`, we have the __option to specify__ _not just mapped entities_ but _ad-hoc SQL expressions_ as well. Suppose if a `class A` had _integer_ attributes `.x` and `.y`, we could query for A objects, and additionally the _sum of .x and .y_, as follows

```
q = session.query(A, A.x + A.y)
```

The above query returns tuples of the form (`A object`, `integer`).

An option exists which can apply the _ad-hoc_ `A.x + A.y` _expression_ to the returned A objects instead of as a separate tuple entry; this is the `with_expression()` query option in conjunction with the `query_expression()` attribute mapping. The class is __mapped to include a placeholder attribute__ where any particular SQL expression may be applied.

We can then query for objects of type `A`, applying an _arbitrary SQL expression_ to be populated into `A.expr`.

```
q = session.query(A).options(with_expression(A.expr, A.x + A.y))
```

The `query_expression()` mapping has these caveats:

* On an object where `query_expression()` were _not used to populate the attribute_, the attribute on an object instance will have the value `None`, unless the `query_expression.default_expr` parameter is set to an alternate SQL expression.

* The `query_expression` value __does not populate on an object that is already loaded__. That is, this will not work:

    ```
    obj = session.query(A).first()
    obj = session.query(A).options(with_expression(A.expr, some_expr)).first()
    ```

To ensure the attribute is _re-loaded_, use `Query.populate_existing()`:

    ```
    obj = (
        session.query(A)
        .populate_existing()
        .options(with_expression(A.expr, some_expr))
        .first()
    )
    ```

* The `query_expression` value __does not refresh when the object is expired__. Once the object is expired, either via `Session.expire()` or via the `expire_on_commit` behavior of `Session.commit()`, the _value is removed from the attribute_ and will _return None_ on subsequent access. Only by running a _new_ `Query` that touches the object which includes a new `with_expression()` directive will the attribute be set to a _non-None value_.

* The mapped attribute currently __cannot be applied to other parts of the query__, such as the `WHERE` clause, the `ORDER BY` clause, and make use of the _ad-hoc expression_; that is, this won't work:

    ```
    # won't work
    q = (
        session.query(A)
        .options(with_expression(A.expr, A.x + A.y))
        .filter(A.expr > 5)
        .order_by(A.expr)
    )
    ```

The `A.expr` expression will resolve to `NULL` in the above `WHERE` clause and `ORDER BY` clause. To use the expression throughout the query, assign to a variable and use that:

    ```
    a_expr = A.x + A.y
    q = (
        session.query(A)
        .options(with_expression(A.expr, a_expr))
        .filter(a_expr > 5)
        .order_by(a_expr)
    )
    ```
