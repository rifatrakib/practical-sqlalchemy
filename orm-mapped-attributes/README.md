## Changing Attribute Behavior

#### Simple Validators

A quick way to add a __"validation" routine__ to an attribute is to use the `validates()` decorator. An _attribute validator_ can raise an exception, halting the process of _mutating the attribute's value_, or can _change the given value into something different_. _Validators_, like all attribute extensions, are __only called by normal userland code__; they are __not issued when the ORM is populating the object__.

_Validators_ also `receive` _collection append events_, when _items_ are __added to a collection__.

The _validation function_ __by default does not get emitted__ for __collection remove events__, as the typical expectation is that a _value being discarded doesn't require validation_. However, `validates()` supports reception of these events by specifying `include_removes=True` to the decorator. When this _flag is set_, the _validation function_ __must receive an additional boolean argument__ which if True indicates that the operation is a removal.

The case where _mutually dependent validators_ are _linked via a backref_ can also be tailored, using the `include_backrefs=False` option; this option, when set to `False`, __prevents a validation function from emitting__ if the event occurs as a result of a backref.

Above, if we were to assign to `Address.user` as in `some_address.user = some_user`, the `validate_address()` function __would not be emitted__, even though an append occurs to `some_user.addresses` - the event is _caused by a backref_.

Note that the `validates()` decorator is a _convenience function_ built on top of _attribute events_. An application that requires _more control over configuration of attribute change behavior_ can make use of this system, described at `AttributeEvents`.


#### Using Custom Datatypes at the Core Level

A _non-ORM_ means of affecting the value of a column in a way that suits _converting data_ between _how it is represented_ in `Python`, vs. _how it is represented_ in the `database`, can be achieved by __using a custom datatype__ that is applied to the `mapped Table metadata`. This is more common in the case of some style of `encoding/decoding` that occurs both as _data goes to the database and as it is returned_; read more about this in the `Core documentation at Augmenting Existing Types`.


#### Using Descriptors and Hybrids

A _more comprehensive way_ to produce _modified behavior_ for an attribute is __to use descriptors__. These are commonly used in Python using the `property()` function. The standard SQLAlchemy technique for descriptors is to __create a plain descriptor__, and to have it _read/write from a mapped attribute with a different name_.

The approach above will work, but there's more we can add. While our `EmailAddressWithProperty` object will __shuttle the value__ through the _email descriptor_ and into the *_email mapped attribute*, the _class level_ `EmailAddressWithProperty.email` _attribute_ __does not have the usual expression semantics usable with `Query`__. To provide these, we instead use the `hybrid extension`.

The `.email` attribute, in addition to providing _getter/setter behavior_ when we have an instance of `EmailAddressHybridExtension`, also _provides a SQL expression_ when __used at the class level__, that is, from the `EmailAddressHybridExtension` class __directly__.

```
address = (
    session.query(EmailAddressHybridExtension).
    filter(
        EmailAddressHybridExtension.email == "address@example.com"
    ).one()
)
```

The `hybrid_property` also allows us to __change the behavior of the attribute__, including _defining separate behaviors_ when the attribute is _accessed at the instance level_ versus at the _class/expression level_, using the `hybrid_property.expression()` _modifier_. Such as, if we wanted to _add a host name automatically_, we might define __two sets of string manipulation logic__.

Above, accessing the _email_ property of an instance of `EmailAddressPropertyExpression` will return the value of the *_email* attribute, __removing or adding the hostname__ `@example.com` from the value. When we _query against the email attribute_, a __SQL function is rendered__ which produces the _same effect_.

```
sqladdress = (
    session.query(EmailAddressPropertyExpression).
    filter(EmailAddressPropertyExpression.email == "address").one()
)
```


#### Synonyms

_Synonyms_ are a __mapper-level construct__ that allow any attribute on a class to `"mirror"` another attribute that is mapped. In the most basic sense, the _synonym_ is an _easy way_ to __make a certain attribute available__ by an _additional name_.

```
class JobStatus(Base):
    __tablename__ = "my_table"
    
    id = Column(Integer, primary_key=True)
    job_status = Column(String(50))
    
    status = synonym("job_status")
```

The above class `JobStatus` has _two attributes_, `.job_status` and `.status` that will __behave as one attribute__, both at the _expression level_:

```
print(JobStatus.job_status == "some_status")
print(JobStatus.status == "some_status")
```

and at the instance level:

```
m1 = JobStatus(status="x")
m1.status, m1.job_status

m1.job_status = "y"
m1.status, m1.job_status
```

The `synonym()` can be used for _any kind of mapped attribute that subclasses_ `MapperProperty`, including _mapped columns_ and _relationships_, as well as _synonyms themselves_.

Beyond a simple mirror, `synonym()` can also be made to __reference a user-defined descriptor__. We can supply our `status` synonym with a `@property`.

```
class StatusProperty(Base):
    __tablename__ = "status_property"
    
    id = Column(Integer, primary_key=True)
    status = Column(String(50))
    
    @property
    def job_status(self):
        return f"Status: {self.status}"
    
    job_status = synonym("status", descriptor=job_status)
```

When using _Declarative_, the above pattern __can be expressed more succinctly__ using the `synonym_for()` decorator.

While the `synonym()` is _useful for simple mirroring_, the use case of _augmenting attribute behavior with descriptors_ is _better handled_ in modern usage using the __hybrid attribute feature__, which is more oriented towards Python descriptors. Technically, a `synonym()` can do everything that a `hybrid_property` can do, as it also supports injection of custom SQL capabilities, but the `hybrid` is __more straightforward__ to use in more complex situations.


##### map_column

__For classical mappings and mappings against an existing Table object only__, if `True`, the `synonym()` construct will _locate_ the `Column` object upon the _mapped table_ that would _normally be associated with the attribute name_ of this synonym, and produce a _new_ `ColumnProperty` that instead maps this `Column` to the alternate name given as the _"name"_ argument of the `synonym`; in this way, the usual step of _redefining the mapping_ of the `Column` to be _under a different name_ is __unnecessary__. This is usually intended to be used when a `Column` is to be _replaced with an attribute that also uses a descriptor_, that is, in conjunction with the `synonym.descriptor` parameter.

```
mapped_table = Table(
    "mapped_table",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("job_status", String(50))
)


class MappedTable:
    @property
    def _job_status_descriptor(self):
        return f"Status: {self._job_status}"


mapper.map_imperatively(
    MappedTable, mapped_table,
    properties={
        "job_status": synonym(
            "_job_status", map_column=True,
            descriptor=MappedTable._job_status_descriptor,
        )
    }
)
```

Above, the attribute named `_job_status` is __automatically mapped__ to the *job_status* column:

```
j1 = MappedTable()
j1._job_status = "employed"
j1.job_status
```

When using _Declarative_, in order to _provide a descriptor in conjunction with a synonym_, use the `sqlalchemy.ext.declarative.synonym_for()` helper. However, note that the _hybrid properties feature_ should usually be __preferred__, particularly when _redefining attribute behavior_.


#### Operator Customization

The `"operators"` used by the _SQLAlchemy ORM_ and _Core expression language_ are __fully customizable__. For example, the comparison expression `User.name == "ed"` makes usage of an operator built into Python itself called `operator.eq` - __the actual SQL construct which SQLAlchemy associates with such an operator can be modified__. New operations can be associated with column expressions as well. The operators which take place for column expressions are most directly redefined at the type level.

_ORM level functions_ like `column_property()`, `relationship()`, and `composite()` also provide for __operator redefinition__ at the ORM level, by passing a `PropComparator` subclass to the `comparator_factory` argument of each function. Customization of operators at this level is a rare use case.
