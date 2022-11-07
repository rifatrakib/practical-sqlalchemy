## Composing Mapped Hierarchies with Mixins

A common need when _mapping classes using the Declarative style_ is to __share some functionality__, such as a `set of common columns`, `some common table options`, or `other mapped properties`, __across many classes__. The __standard Python idioms__ for this is to have the __classes inherit from a superclass__ which _includes these common features_.

When _using declarative mappings_, this idiom is __allowed via the usage of mixin classes__, as well as __via augmenting the declarative base__ produced by either the `registry.generate_base()` method or `declarative_base()` functions.

When using _mixins_ or _abstract base classes_ with `Declarative`, a _decorator_ known as `declared_attr()` is __frequently used__. This _decorator_ allows the __creation of class methods__ that _produce a parameter or ORM construct_ that will be part of a _declarative mapping_. _Generating constructs using a callable_ allows for `Declarative` to get a _new copy of a particular kind of object each time it calls_ upon the `mixin` or `abstract base` on behalf of a __new class that's being mapped__.

Where above, the class `UserModel` will contain an `"id"` column as the `primary key`, a `__tablename__` attribute that __derives from the name of the class itself__, as well as `__table_args__` and `__mapper_args__` defined by the `CustomMixin` _mixin class_. The `declared_attr()` _decorator_ applied to a _classmethod_ called `def __tablename__(cls):` has the effect of _turning the method into a classmethod_ while also indicating to `Declarative` that _this attribute_ is __significant within the mapping__.


> ##### Tip
> 
> The use of the `declarative_mixin()` _class decorator_ __marks a particular class as providing the service of providing SQLAlchemy declarative assignments__ as a mixin for other classes. This decorator is _currently only necessary to provide a hint to the Mypy plugin_ that this class should be handled as part of __declarative mappings__.

There's __no fixed convention__ over whether __`CustomMixin` precedes `Base` or not__. _Normal Python method resolution rules_ __apply__, and the above example would work just as well with:

```
class UserModel(Base, CustomMixin):
    age = Column(Integer)
```

This works because `Base` here __doesn't define any of the variables that `CustomMixin` defines__, i.e. `__tablename__`, `__table_args__`, `id`, etc. __If the `Base` did define an attribute of the same name__, the _class placed first_ in the _inherits list_ would __determine which attribute is used__ on the _newly defined class_.


#### Augmenting the Base

In addition to using a _pure mixin_, most of the techniques in this section _can also be applied_ to the `base class` itself, for _patterns_ that should apply to all classes __derived from a particular base__. This is achieved using the _cls argument_ of the `declarative_base()` function.

Where above, `MyModel` and _all other classes_ that __derive from `Base`__ will have a _table name_ __derived from the class name__, an `id` _primary key column_, as well as the `"InnoDB"` _engine for MySQL_.
