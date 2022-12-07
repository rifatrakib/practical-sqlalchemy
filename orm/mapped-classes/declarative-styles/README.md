## Declarative Mapping Styles

As introduced at `Declarative Mapping`, the __Declarative Mapping__ is the _typical_ way that mappings are constructed in `modern SQLAlchemy`. This section will provide an overview of forms that may be used for _Declarative mapper configuration_.


#### Using a Generated Base Class

The _most common approach_ is to generate a __"base" class__ using the `declarative_base()` function.

The _declarative base class_ may also be __created from an existing registry__, by using the `registry.generate_base()` method.

With the _declarative base class_, `new mapped classes` are declared as __subclasses of the base__.

Above, the `declarative_base()` function returns a __new base class__ from which _new classes to be mapped_ __may `inherit` from__, as above a _new mapped class_ `User` is constructed.

For _each subclass_ constructed, the body of the class then follows the `declarative mapping approach` which defines both a `Table` as well as a `Mapper` object __behind the scenes__ which _comprise a full mapping_.


#### Creating an Explicit Base Non-Dynamically (for use with mypy, similar)

`SQLAlchemy` includes a `Mypy` _plugin_ that __automatically accommodates__ for the _dynamically generated_ `Base` class delivered by `SQLAlchemy` functions like `declarative_base()`. For the __SQLAlchemy 1.4 series only__, this _plugin_ works along with a _new set of typing stubs_ published at `sqlalchemy2-stubs`.

When this _plugin_ is `not in use`, or when _using other PEP 484 tools_ which _may not know_ how to _interpret_ this class, the `declarative base class` may be produced in a __fully explicit fashion__ using the `DeclarativeMeta` __directly__.

The `Base` class created as such is _equivalent to one created using_ the `registry.generate_base()` method and will be __fully understood by type analysis tools__ _without the use of plugins_.


#### Declarative Mapping using a Decorator (no declarative base)

As an _alternative_ to using the `"declarative base"` class is to __apply declarative mapping__ to a class __`explicitly`__, using either an _imperative technique_ __similar__ to that of a `"classical" mapping`, or _more succinctly_ by __using a `decorator`__. The `registry.mapped()` function is a __class decorator__ that _can be applied_ to _any Python class with no hierarchy_ in place. The _Python class otherwise is configured_ in __declarative style normally__.

Above, the _same registry_ that we'd use to _generate_ a `declarative base class` via its `registry.generate_base()` method _may also apply a declarative-style mapping_ to a class __without using a base__. When using the above style, the _mapping_ of a particular class will __only proceed__ if the `decorator` is __applied to that class directly__. For _inheritance mappings_, the `decorator` should be __applied to each subclass__.

Both the `declarative table` and `imperative table` styles of _declarative mapping_ __may be used__ with the _above mapping style_.

The `decorator form` of _mapping_ is __particularly useful__ when _combining_ a `SQLAlchemy declarative mapping` with _other forms of class declaration_, `notably` the __Python `dataclasses` module__.
