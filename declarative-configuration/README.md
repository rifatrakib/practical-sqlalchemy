## Mapper Configuration with Declarative

The section `Mapped Class Essential Components` discusses the _general configurational elements_ of a `Mapper` construct, which is the _structure_ that defines __how a particular user defined class is mapped to a database table or other SQL construct__. The following sections describe specific details about how the _declarative system_ goes about _constructing_ the `Mapper`.


#### Defining Mapped Properties with Declarative

The examples given at `Table Configuration with Declarative` illustrate _mappings against table-bound columns_; the _mapping_ of an _individual column_ to an `ORM class attribute` is __represented internally__ by the `ColumnProperty` construct. There are _many other varieties_ of `mapper` properties, the _most common_ being the `relationship()` construct. Other kinds of properties include _synonyms to columns_ which are defined using the `synonym()` construct, SQL expressions that are defined using the `column_property()` construct, and _deferred columns_ and `SQL expressions` which _load only when accessed_, defined using the `deferred()` construct.

While an _imperative mapping_ makes use of the `properties dictionary` to establish all the __mapped class attributes__, in the _declarative mapping_, these properties are all __specified inline__ with the _class definition_, which in the case of a _declarative table mapping_ are __inline__ with the `Column` objects that will be used to _generate_ a `Table` object.

Working with the example mapping of `User` and `Address`, we may illustrate a _declarative table mapping_ that __includes not just `Column` objects but also `relationships` and `SQL` expressions__.
