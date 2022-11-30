## Changing Attribute Behavior

#### Simple Validators

A quick way to add a __"validation" routine__ to an attribute is to use the `validates()` decorator. An _attribute validator_ can raise an exception, halting the process of _mutating the attribute's value_, or can _change the given value into something different_. _Validators_, like all attribute extensions, are __only called by normal userland code__; they are __not issued when the ORM is populating the object__.

_Validators_ also `receive` _collection append events_, when _items_ are __added to a collection__.

The _validation function_ __by default does not get emitted__ for __collection remove events__, as the typical expectation is that a _value being discarded doesn't require validation_. However, `validates()` supports reception of these events by specifying `include_removes=True` to the decorator. When this _flag is set_, the _validation function_ __must receive an additional boolean argument__ which if True indicates that the operation is a removal.

The case where _mutually dependent validators_ are _linked via a backref_ can also be tailored, using the `include_backrefs=False` option; this option, when set to `False`, __prevents a validation function from emitting__ if the event occurs as a result of a backref.

Above, if we were to assign to `Address.user` as in `some_address.user = some_user`, the `validate_address()` function __would not be emitted__, even though an append occurs to `some_user.addresses` - the event is _caused by a backref_.

Note that the `validates()` decorator is a _convenience function_ built on top of _attribute events_. An application that requires _more control over configuration of attribute change behavior_ can make use of this system, described at `AttributeEvents`.
