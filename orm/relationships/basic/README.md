## Basic Relationship Patterns

A quick walkthrough of the basic relational patterns. The imports used for each of the following sections is as follows:

```
from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
```


#### One To Many

A _one to many relationship_ places a `foreign key` on the _child table_ referencing the _parent_. `relationship()` is then __specified on the parent__, as referencing a _collection of items_ represented by the child.

To establish a __bidirectional relationship__ in _one-to-many_, where the `"reverse"` side is a _many to one_, specify an __additional `relationship()`__ and connect the two using the `relationship.back_populates` parameter.

_Alternatively_, the `relationship.backref` option may be __used on a single `relationship()`__ instead of using `relationship.back_populates`.


##### Configuring Delete Behavior for One to Many

It is often the case that _all Child objects_ should be __deleted__ when their _owning Parent is deleted_. To _configure_ this behavior, the `delete cascade option` described at _delete_ is used. An additional option is that a _Child_ object __can itself be deleted__ when it is _deassociated from its parent_. This behavior is described at `delete-orphan`.


#### Many To One

_Many to one_ places a `foreign key` in the __parent table referencing the child__. `relationship()` is __declared on the parent__, where a _new scalar-holding attribute_ will be created.

_Bidirectional behavior_ is achieved by adding a __second__ `relationship()` and applying the `relationship.back_populates` parameter in __both directions__.

_Alternatively_, the `relationship.backref` parameter may be __applied to a single `relationship()`__, such as `Parent.child`.
