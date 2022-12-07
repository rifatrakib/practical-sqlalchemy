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


#### Mapper Configuration Options with Declarative

With _all_ mapping forms, the `mapping of the class` is __configured through parameters__ that become part of the `Mapper` object. The _function_ which __ultimately receives these arguments__ is the `mapper()` function, and are _delivered_ to it from one of the _front-facing mapping functions_ defined on the `registry` object.

For the _declarative form_ of mapping, mapper arguments are specified using the `__mapper_args__` declarative class variable, which is a __dictionary that is passed as keyword arguments__ to the `mapper()` function.


##### Map Specific Primary Key Columns

The example below illustrates _Declarative-level settings_ for the `mapper.primary_key` parameter, which __establishes__ particular columns as part of what the `ORM` _should consider_ to be a __primary key for the class__, _independently_ of schema-level `primary key constraints`.


##### Version ID Column

The example below illustrates _Declarative-level settings_ for the `mapper.version_id_col` and `mapper.version_id_generator` parameters, which __configure an ORM-maintained version counter__ that is _updated and checked_ within the unit of work `flush process`.


##### Single Table Inheritance

The example below illustrates _Declarative-level settings_ for the `mapper.polymorphic_on` and `mapper.polymorphic_identity` parameters, which are used when __configuring a single-table inheritance mapping__.


##### Constructing mapper arguments dynamically

The `__mapper_args__` dictionary _may be generated_ from a __class-bound descriptor method__ rather than from a _fixed dictionary_ by making use of the `declared_attr()` construct. This is __useful to create arguments for mappers that are programmatically derived__ from the _table configuration or other aspects_ of the `mapped class`. A __dynamic `__mapper_args__` attribute__ will typically be useful when using a `Declarative Mixin` or `abstract base class`.

For example, to __omit from the mapping__ _any columns that have a special_ `Column.info` value, a _mixin_ can use a `__mapper_args__` method that __scans for these columns__ from the `cls.__table__` attribute and passes them to the `mapper.exclude_properties` collection.

Above, the `ExcludeColsWFlag` _mixin_ provides a __per-class `__mapper_args__` hook__ that will _scan_ for `Column` objects that __include the `key/value` `"exclude": True`__ passed to the `Column.info` parameter, and then add their string `"key"` name to the `mapper.exclude_properties` collection which will __prevent the resulting `Mapper` from considering these columns__ for any SQL operations.


#### Other Declarative Mapping Directives

* `__declare_last__()`: The `__declare_last__()` _hook_ __allows definition of a class level function__ that is _automatically called_ by the `MapperEvents.after_configured()` event, which occurs __after mappings are assumed to be completed__ and the __`"configure"` step has finished__.

* `__declare_first__()`: Like `__declare_last__()`, but is called at the __beginning of mapper configuration__ via the `MapperEvents.before_configured()` event.

* `metadata`: The `MetaData` collection _normally used to assign_ a __new `Table`__ is the `registry.metadata` attribute _associated with_ the `registry` object in use. When using a _declarative base class_ such as that __generated__ by `declarative_base()` as well as `registry.generate_base()`, this `MetaData` is also _normally present_ also as an _attribute_ named `.metadata` that's __directly on the base class__, and thus also on the __mapped class via inheritance__. _Declarative uses this attribute_, when present, in order to __determine the target `MetaData` collection__, or if _not present_, uses the `MetaData` __associated directly with the registry__.

This _attribute_ may also be _assigned towards_ in order to __affect the `MetaData` collection__ to be used on a __per-mapped-hierarchy basis for a single base and/or registry__. This _takes effect whether a declarative base class is used_ or if the `registry.mapped()` _decorator is used directly_, thus _allowing patterns_ such as the `metadata-per-abstract base` example in the next section, `__abstract__`. A _similar pattern_ can be illustrated using `registry.mapped()` as follows.

* `__abstract__`: `__abstract__` causes declarative to _skip the production of a table or mapper_ for the class __entirely__. A _class can be added within a hierarchy_ in the same way as `mixin` (see `Mixin and Custom Base Classes`), __allowing subclasses to extend just from the special class__. _One possible use_ of `__abstract__` is to __use a distinct `MetaData` for different bases__.

Above, _classes which inherit from_ `DefaultBase` will use one `MetaData` as the __registry of tables__, and _those which inherit from_ `OtherBase` will __use a different one__. The _tables themselves_ can then be __created perhaps within distinct databases__.

```
DefaultBase.metadata.create_all(engine_one)
OtherBase.metadata.create_all(engine_two)
```

* `__table_cls__`: Allows the _callable/class_ used to _generate_ a `Table` to be __customized__. This is a very `open-ended hook` that can __allow special customizations__ to a `Table` that one generates here.

The above _mixin_ would cause _all_ `Table` _objects_ generated to __include the prefix `"custom_"`, followed by the name__ normally specified using the `__tablename__` attribute.

`__table_cls__` also _supports_ the case of _returning_ `None`, which _causes the class_ to be __considered as single-table inheritance vs. its subclass__. This _may be useful in some customization schemes_ to determine that `single-table inheritance` should take place based on the _arguments for the table itself_, such as, define as _single-inheritance_ if there is __no primary key present__.

The above `Employee` class would be __mapped as single-table inheritance against__ `Person`; the `employee_name` column would be _added as a member_ of the `Person` table.
