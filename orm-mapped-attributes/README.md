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
