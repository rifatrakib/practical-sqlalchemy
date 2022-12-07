## ORM Mapping Styles

`SQLAlchemy` features _two distinct styles_ of __mapper configuration__, which then _feature further sub-options_ for how they are _set up_. The _variability_ in `mapper styles` is present to __suit a varied list of developer preferences__, including the _degree of abstraction of a user-defined class_ from how it is to be `mapped to relational schema tables and columns`, what `kinds of class hierarchies` are in use, including whether or not `custom metaclass schemes` are present, and finally if there are other _class-instrumentation approaches_ present such as if `Python dataclasses` are in use _simultaneously_.

In `modern SQLAlchemy`, the _difference_ between these styles is __mostly superficial__; when a particular `SQLAlchemy configurational style` is used to __express the intent to map a class__, the _internal process_ of __mapping the class__ proceeds in __`mostly the same way`__ for each, where the _end result_ is __always__ a `user-defined class` that has a `Mapper` __configured__ against a _selectable unit_, typically represented by a `Table` object, and the _class itself_ has been __instrumented__ to include `behaviors linked to relational operations` both at the level of the `class` as well as on `instances of that class`. As the _process_ is __basically the same__ in all cases, _classes mapped from different styles_ are __always `fully` interoperable__ with each other.

The _original mapping API_ is commonly referred to as `"classical" style`, whereas the _more automated style of mapping_ is known as `"declarative" style`. `SQLAlchemy` now refers to these _two mapping styles_ as _`imperative mapping`_ and `declarative mapping`.

_Regardless_ of what style of mapping used, _all ORM mappings_ as of `SQLAlchemy 1.4` __originate from a single object__ known as `registry`, which is a __registry of mapped classes__. Using this `registry`, a `set of mapper configurations` can be _finalized_ as a group, and `classes within a particular registry` may __refer to each other by name__ within the `configurational process`.


#### Declarative Mapping

The `Declarative Mapping` is the __typical way__ that `mappings` are constructed in _modern SQLAlchemy_. The __most common pattern__ is to _first_ construct `a base class` using the `declarative_base()` function, which will __apply__ the `declarative mapping process` to _all subclasses_ that __`derive` from it__.

Above, the `declarative_base()` __callable__ returns a `new base class` from which _new classes to be mapped_ may __inherit from__, as above a _new mapped class_ `User` is constructed.

The _base class_ refers to a `registry object` that __maintains a collection of related mapped classes__. The `declarative_base()` function is in fact __shorthand__ for first _creating_ the `registry` with the _registry constructor_, and then __generating a base class__ using the `registry.generate_base()` method.

The _major_ `Declarative mapping styles` are further detailed in the following sections:

* __Using a Generated Base Class__ - `declarative mapping` using a _base class_ __generated__ by the `registry` object.

* __Declarative Mapping using a Decorator__ (_no declarative base_) - `declarative mapping` using a _decorator_, rather than a _base class_.

_Within the scope_ of a `Declarative mapped class`, there are also _two varieties_ of how the `Table metadata` may be declared. These include:

* __Declarative Table__ - _individual Column definitions_ are __combined__ with a `table name` and `additional arguments`, where the `Declarative mapping` process will construct a `Table` object to be _mapped_.

* __Declarative with Imperative Table__ (a.k.a. _Hybrid Declarative_) - Instead of specifying `table name` and `attributes` separately, an __explicitly__ constructed `Table` object is __associated with a class__ that is _otherwise mapped declaratively_. This style of mapping is a __hybrid of `"declarative"` and `"imperative"` mapping__.


#### Imperative Mapping

An _imperative or classical mapping_ refers to the `configuration of a mapped class` using the `registry.map_imperatively()` method, where the _target class_ __does not include any declarative class attributes__. The `"map imperative"` style has _historically_ been achieved using the `mapper()` function __directly__, however this function _now expects_ that a `sqlalchemy.orm.registry()` is present.

In `"classical"` form, the `table metadata` is __created separately__ with the `Table` construct, then _associated_ with the `User` class via the `registry.map_imperatively()` method.

`Information` about _mapped attributes_, such as `relationships` to other classes, are __provided via the properties dictionary__. The example below illustrates a second `Table` object, _mapped_ to a class called `Address`, then __linked to `User`__ via `relationship()`.

When using _classical mappings_, classes must be provided __directly without the benefit of the string lookup system__ provided by `Declarative`. SQL expressions are _typically specified_ in terms of the `Table` objects, i.e. `address.c.id` above for the `Address` relationship, and not `Address.id`, as `Address` _may not yet be linked to table metadata_, __nor can we specify a string here__.

Some examples in the documentation still use the _classical approach_, but note that the `classical` as well as `Declarative approaches` are __fully interchangeable__. `Both` systems _ultimately create the same configuration_, consisting of a `Table`, _user-defined class_, __linked together__ with a `mapper()`. When we talk about __"the behavior of `mapper()`"__, this includes when using the `Declarative system` as well - it's _still used_, just __behind the scenes__.


#### Mapped Class Essential Components

With all mapping forms, the _mapping of the class_ can be __configured__ in _many ways_ by __passing construction arguments__ that become part of the `Mapper` object. The _function_ which __ultimately receives__ these arguments is the `mapper()` function, which are _delivered_ to it _originating from_ one of the __front-facing mapping functions__ defined on the `registry` object.

There are __`four`__ _general classes_ of __configuration information__ that the `mapper()` function looks for:


##### The class to be mapped

This is a class that we construct in our application. There are __generally no restrictions__ on the _structure of this class_. When a _Python class_ is `mapped`, there __can only be one__ `Mapper` object for the class.

When _mapping_ with the `declarative mapping style`, the _class to be mapped_ is _either a subclass_ of the __declarative base class__, _or is handled_ by a __decorator or function__ such as `registry.mapped()`.

When _mapping_ with the `imperative style`, the class is __passed directly__ as the `map_imperatively.class_` argument.


##### The table, or other from clause object

In the _vast majority_ of common cases this is an _instance_ of `Table`. For more advanced use cases, it __may also refer__ to _any kind_ of `FromClause` object, the __most common alternative__ objects being the `Subquery` and `Join` object.

When _mapping_ with the `declarative mapping style`, the _subject table_ is either _generated_ by the __declarative system__ based on the `__tablename__` attribute and the `Column` objects presented, or it is _established_ via the `__table__` attribute. These _two styles of configuration_ are presented at `Declarative Table` and `Declarative with Imperative Table (a.k.a. Hybrid Declarative)`.

When _mapping_ with the `imperative style`, the _subject table_ is __passed positionally__ as the `map_imperatively.local_table` argument.

In contrast to the __"one mapper per class"__ requirement of a _mapped class_, the `Table` or other `FromClause` object that is the `subject of the mapping` __may be associated__ with _any number of mappings_. The `Mapper` __applies modifications directly__ to the _user-defined class_, but __does not modify__ the given `Table` or other `FromClause` in any way.


##### The properties dictionary

This is a `dictionary` of _all of the attributes_ that will be __associated__ with the `mapped class`. By _default_, the `Mapper` __generates entries__ for this _dictionary derived from_ the given `Table`, in the form of `ColumnProperty` objects which _each refer to an individual_ `Column` of the _mapped table_. The _properties dictionary_ will _also contain_ all the other kinds of `MapperProperty` objects to be _configured_, __most commonly__ instances generated by the `relationship()` construct.

When _mapping_ with the `declarative mapping style`, the _properties dictionary_ is generated by the `declarative system` by __scanning the class to be mapped__ for _appropriate attributes_. See the section `Defining Mapped Properties with Declarative` for notes on this process.

When _mapping_ with the `imperative style`, the _properties dictionary_ is __passed directly__ as the properties argument to `registry.map_imperatively()`, which will _pass it along_ to the `mapper.properties` parameter.


##### Other mapper configuration parameters

When _mapping_ with the `declarative mapping style`, _additional mapper configuration_ arguments are __configured__ via the `__mapper_args__` class attribute. Examples of use are available at `Mapper Configuration Options with Declarative`.

When _mapping_ with the `imperative style`, _keyword arguments_ are passed to the to `registry.map_imperatively()` method which __passes them along__ to the `mapper()` function.


#### Mapped Class Behavior

Across all styles of _mapping_ using the `registry` object, the following behaviors are common.


##### Default Constructor

The `registry` applies a _default constructor_, i.e. `__init__` method, to _all mapped classes_ that __don't explicitly have their own `__init__` method__. The _behavior_ of this method is such that it __provides a convenient keyword constructor__ that _will accept_ as `optional keyword arguments` all the attributes that are named.

An object of type `DeclarativeUser` above will have a __constructor__ which allows `DeclarativeUser` objects to be created.

```
u1 = DeclarativeUser(name="some name", fullname="some fullname")
```

The above _constructor_ may be __customized__ by passing a _Python callable_ to the `registry.constructor` parameter which provides the __desired default `__init__()` behavior__.

The _constructor_ __also applies__ to `imperative mappings`.

The above class, _mapped imperatively_ as described at `Imperative Mapping`, will _also feature_ the `default constructor` __associated__ with the `registry`.


##### Runtime Introspection of Mapped classes, Instances and Mappers

A _class_ that is __mapped using `registry`__ will also _feature a few attributes_ that are __common to all mappings__.

* The `__mapper__` attribute will _refer to_ the `Mapper` that is __associated__ with the class. This `Mapper` is also what's _returned_ when using the `inspect()` function against the _mapped class_.

* The `__table__` attribute will _refer to_ the `Table`, or _more generically_ to the `FromClause` object, to which the class is __mapped__. This `FromClause` is also what's _returned_ when using the `Mapper.local_table` attribute of the `Mapper`.

For a `single-table inheritance mapping`, where the _class is a subclass_ that __does not have a table of its own__, the `Mapper.local_table` attribute as well as the `.__table__` attribute will be __`None`__. __To retrieve the `"selectable"`__ that is _actually selected_ from during a query for this class, this is __available via__ the `Mapper.selectable` attribute.


##### Inspection of Mapper objects

As illustrated in the previous section, the `Mapper` object is __available from any mapped class__, regardless of method, using the `Runtime Inspection API` system. Using the `inspect()` function, one __can acquire__ the `Mapper` from a _mapped class_. _Detailed information_ is available including `Mapper.columns`. This is a _namespace_ that __can be viewed in a list format__ or __via individual names__. _Other namespaces_ include `Mapper.all_orm_descriptors`, which __includes all mapped attributes__ as well as __hybrids__, _association proxies_ as well as `Mapper.column_attrs`.


##### Inspection of Mapped Instances

The `inspect()` function also _provides information_ about instances of a `mapped class`. When applied to an instance of a _mapped class_, rather than the class itself, the _object returned_ is known as `InstanceState`, which will _provide links_ to not only the __`Mapper` in use by the class__, but also a __detailed interface__ that provides information on the _state of individual attributes_ within the instance __including__ their `current value` and how this relates to what `their database-loaded value` is.

Given an instance of the `User` class __loaded from the database__, the `inspect()` function will return to us an `InstanceState` object. With this object we can see _elements_ such as the `Mapper`, the `Session` to which the object is __attached__, if any, and _information_ about the `current persistence state` for the object. `Attribute state information` such as attributes that __have not been loaded__ or __lazy loaded__ (assume _addresses_ refers to a `relationship()` on the _mapped class to a related class_).

Information regarding the __current `in-Python` status of attributes__, such as attributes that `have not been modified` _since the last_ `flush` as well as _specific history_ on __modifications to attributes__ since the `last flush`.
