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


#### Composite Adjacency Lists

A _sub-category_ of the _adjacency list relationship_ is the rare case where a __particular column is present__ on both the `"local"` and `"remote"` side of the _join condition_. An example is the _Folder_ class below; using a `composite primary key`, the *account_id* column __refers to itself__, to indicate __sub folders which are within the same account as that of the parent__; while *folder_id* refers to a __specific folder within that account__.

```
class Folder(Base):
    __tablename__ = "folder"
    __table_args__ = (
        ForeignKeyConstraint(
            ["account_id", "parent_id"],
            ["folder.account_id", "folder.folder_id"],
        ),
    )
    
    account_id = Column(Integer, primary_key=True)
    folder_id = Column(Integer, primary_key=True)
    parent_id = Column(Integer)
    name = Column(String)
    
    parent_folder = relationship(
        "Folder", backref="child_folders",
        remote_side=[account_id, folder_id],
    )
```

Above, we pass *account_id* into the `relationship.remote_side` list. `relationship()` recognizes that the *account_id* column here is __on both sides__, and aligns the `"remote"` column along with the *folder_id* column, which it __recognizes as uniquely present__ on the `"remote"` side.


#### Self-Referential Query Strategies

Querying of _self-referential structures_ works like any other query:

```
# get all nodes named 'child2'
session.query(Node).filter(Node.data == "child2")
```

However _extra care_ is needed when _attempting to join along the foreign key from one level of the tree to the next_. In SQL, a _join_ from a table to itself __requires__ that __at least one side of the expression be `"aliased"`__ so that it can be __unambiguously referred__ to.

Recall from `Selecting ORM Aliases` in the ORM tutorial that the `aliased()` construct is normally used to provide an `"alias"` of an ORM entity. Joining from _Node_ to itself using this technique looks like:

```
from sqlalchemy.orm import aliased

nodealias = aliased(Node)
session.query(Node).filter(Node.data == "subchild1").join(
    Node.parent.of_type(nodealias)
).filter(nodealias.data == "child2").all()
SELECT node.id AS node_id,
        node.parent_id AS node_parent_id,
        node.data AS node_data
FROM node JOIN node AS node_1
    ON node.parent_id = node_1.id
WHERE node.data = ?
    AND node_1.data = ?
['subchild1', 'child2']
```


#### Configuring Self-Referential Eager Loading

_Eager loading_ of relationships occurs using _joins_ or _outerjoins_ from parent to child table during a _normal query operation_, such that the _parent_ and its _immediate child collection or reference_ can be __populated from a single SQL statement__, or a __second statement for all immediate child collections__. SQLAlchemy's _joined and subquery eager loading_ use aliased tables in all cases when _joining to related items_, so are __compatible__ with `self-referential joining`. However, to use _eager loading with a self-referential relationship_, SQLAlchemy __needs to be told how many levels deep it should join and/or query__; otherwise the _eager load_ will __not take place at all__. This depth setting is configured via `relationships.join_depth`:

```
class Node(Base):
    __tablename__ = "node"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("node.id"))
    data = Column(String(50))
    children = relationship("Node", lazy="joined", join_depth=2)


session.query(Node).all()
SELECT node_1.id AS node_1_id,
        node_1.parent_id AS node_1_parent_id,
        node_1.data AS node_1_data,
        node_2.id AS node_2_id,
        node_2.parent_id AS node_2_parent_id,
        node_2.data AS node_2_data,
        node.id AS node_id,
        node.parent_id AS node_parent_id,
        node.data AS node_data
FROM node
    LEFT OUTER JOIN node AS node_2
        ON node.id = node_2.parent_id
    LEFT OUTER JOIN node AS node_1
        ON node_2.id = node_1.parent_id
[]
```
