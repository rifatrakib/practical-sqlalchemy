## Adjacency List Relationships

The _adjacency list pattern_ is a common _relational pattern_ whereby a table contains a __foreign key reference to itself__, in other words is a `self referential relationship`. This is the most common way to represent _hierarchical data in flat tables_. Other methods include _nested sets_, sometimes called __"modified preorder"__, as well as _materialized path_. Despite the appeal that _modified preorder_ has when evaluated for its fluency within SQL queries, the _adjacency list model_ is probably the __most appropriate pattern for the large majority of hierarchical storage needs__, for reasons of _concurrency_, _reduced complexity_, and that _modified preorder has little advantage_ over an application which can __fully load subtrees into the application space__.

With this structure, a graph such as the following:

```
root --+---> child1
       +---> child2 --+--> subchild1
       |              +--> subchild2
       +---> child3
```

Would be represented with data such as:

```
id       parent_id     data
---      -------       ----
1        NULL          root
2        1             child1
3        1             child2
4        3             subchild1
5        3             subchild2
6        1             child3
```

The `relationship()` configuration here works in the same way as a __`"normal"` one-to-many relationship__, with the exception that the `"direction"`, i.e. whether the _relationship_ is _one-to-many_ or _many-to-one_, is assumed __by default__ to be _one-to-many_. To establish the relationship as _many-to-one_, an __extra directive is added__ known as `relationship.remote_side`, which is a _Column_ or _collection of Column_ objects that indicate those which should be considered to be `"remote"`.

Where above, the _id_ column is applied as the `relationship.remote_side` of the __parent__ `relationship()`, thus establishing *parent_id* as the `"local"` side, and the _relationship_ then behaves as a _many-to-one_.

As always, __both directions can be combined into a bidirectional relationship__ using the `backref()` function.
