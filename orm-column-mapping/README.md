## Mapping Table Columns

Introductory background on _mapping to columns_ falls under the subject of `Table configuration`; the general form falls under one of __three forms__:

* `Declarative Table` - `Column` objects are _associated with_ a `Table` as well as with an `ORM mapping` in one step by __declaring them inline as class attributes__.

* `Declarative with Imperative Table` (a.k.a. _Hybrid Declarative_) - `Column` objects are __associated directly__ with their `Table` object, as detailed at `Describing Databases with MetaData`; the _columns_ are then __mapped__ by the _Declarative process_ by __associating__ the `Table` with the _class to be mapped_ via the `__table__` attribute.

* `Imperative Mapping` - like __`"Imperative Table"`__, `Column` objects are __associated directly__ with their `Table` object; the _columns_ are then __mapped__ by the `Imperative process` using `registry.map_imperatively()`.

In all of the above cases, the _mapper constructor_ is ultimately invoked with a completed `Table` object __passed as the selectable unit to be mapped__. The _behavior of mapper_ then is to __assemble all the columns__ in the mapped `Table` into _mapped object attributes_, each of which are __named according to the name of the column__ itself (specifically, the _key attribute_ of `Column`). This behavior _can be modified in several ways_.


#### Naming Columns Distinctly from Attribute Names

A mapping _by default shares the same name_ for a `Column` as that of the _mapped attribute_ - specifically it matches the `Column.key` attribute on `Column`, which __by default is the same__ as the `Column.name`.

The _name_ assigned to the Python attribute which __maps__ to `Column` __can be different__ from either `Column.name` or `Column.key` __just by assigning it that way__, as we illustrate here in a `Declarative mapping`.

Where above `User.id` resolves to a column named `user_id` and `User.name` resolves to a column named `user_name`.

When _mapping to an existing table_, the `Column` object __can be referenced directly__.

The corresponding technique for an _imperative mapping_ is to __place the desired key__ in the `mapper.properties` dictionary with the desired key.


#### Automating Column Naming Schemes from Reflected Tables

In the previous section `Naming Columns Distinctly from Attribute Names`, we showed how a `Column` __explicitly mapped__ to a class can have a _different attribute name_ than the column. But what if we aren't listing out `Column` objects _explicitly_, and instead are _automating_ the production of `Table` objects using __reflection__ (i.e. as described in `Reflecting Database Objects`)? In this case we can make use of the `DDLEvents.column_reflect()` event to __intercept the production of `Column` objects__ and provide them with the `Column.key` of our choice. The event is __most easily associated__ with the `MetaData` object that's in use, such as below we use the one linked to the `declarative_base` instance.

With the above _event_, the _reflection_ of `Column` objects will be __intercepted with our event__ that _adds_ a new `".key"` element, such as in a mapping as below.

The approach also works with both the `DeferredReflection` base class as well as with the `Automap extension`. _For automap specifically_, see the section `Intercepting Column Definitions` for background.


#### Using column_property for column level options

_Options_ can be specified when mapping a `Column` using the `column_property()` function. This function __explicitly creates the `ColumnProperty`__ used by the `mapper()` to __keep track of the `Column`__; normally, the `mapper()` creates this __automatically__. Using `column_property()`, we can _pass additional arguments_ about how we'd like the `Column` to be mapped. Below, we pass an option *active_history*, which specifies that a change to this column's value should result in the former value being loaded first.

`column_property()` is also used to __map a single attribute to multiple columns__. This use case arises when _mapping to_ a `join()` which has attributes which are equated to each other.

Another place where `column_property()` is needed is to __specify SQL expressions as mapped attributes__, such as below where we _create an attribute_ fullname that is the _string concatenation_ of the `firstname` and `lastname` columns.
