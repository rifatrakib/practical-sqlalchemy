## Mapper Configuration with Declarative

The section `Mapped Class Essential Components` discusses the _general configurational elements_ of a `Mapper` construct, which is the _structure_ that defines __how a particular user defined class is mapped to a database table or other SQL construct__. The following sections describe specific details about how the _declarative system_ goes about _constructing_ the `Mapper`.


#### Defining Mapped Properties with Declarative

The examples given at `Table Configuration with Declarative` illustrate _mappings against table-bound columns_; the _mapping_ of an _individual column_ to an `ORM class attribute` is __represented internally__ by the `ColumnProperty` construct. There are _many other varieties_ of `mapper` properties, the _most common_ being the `relationship()` construct. Other kinds of properties include _synonyms to columns_ which are defined using the `synonym()` construct, SQL expressions that are defined using the `column_property()` construct, and _deferred columns_ and `SQL expressions` which _load only when accessed_, defined using the `deferred()` construct.

While an _imperative mapping_ makes use of the `properties dictionary` to establish all the __mapped class attributes__, in the _declarative mapping_, these properties are all __specified inline__ with the _class definition_, which in the case of a _declarative table mapping_ are __inline__ with the `Column` objects that will be used to _generate_ a `Table` object.

Working with the example mapping of `User` and `Address`, we may illustrate a _declarative table mapping_ that __includes not just `Column` objects but also `relationships` and `SQL` expressions__.

The above _declarative table mapping_ features two tables, each with a `relationship()` referring to the other, as well as a __simple `SQL` expression__ _mapped_ by `column_property()`, and an _additional_ `Column` that will be __loaded on a `"deferred"` basis__ as defined by the `deferred()` construct. More documentation on these particular concepts may be found at `Basic Relationship Patterns`, `Using column_property`, and `Deferred Column Loading`.

Properties may be specified with a _declarative mapping_ as above using __"hybrid table" style__ as well; the `Column` objects that are __directly part of a table__ move into the `Table` definition but everything else, including composed SQL expressions, would __still be inline__ with the class definition. _Constructs_ that _need to refer_ to a `Column` __directly__ would reference it in terms of the `Table` object. To illustrate the above mapping using _hybrid table style_.

Things to note above:

* The _address_ `Table` contains a _column_ called `address_statistics`, however we __re-map__ this column under the __same attribute name__ to be under the control of a `deferred()` construct.

* With both _declararative table_ and _hybrid table_ mappings, when we define a `ForeignKey` construct, we _always name the target table_ using the __table name__, and __not the mapped class name__.

* When we define `relationship()` constructs, as these constructs __create a linkage between two mapped classes__ where __one necessarily is defined before the other__, we can refer to the _remote class_ using its __string name__. This _functionality_ also __extends__ into the area of _other arguments_ specified on the `relationship()` such as the `"primary join"` and `"order by"` arguments. See the section `Late-Evaluation of Relationship Arguments` for details on this.
