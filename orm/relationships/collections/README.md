## Collection Configuration and Techniques

The `relationship()` function _defines a linkage between two classes_. When the linkage defines a _one-to-many_ or _many-to-many_ relationship, it's represented as a _Python collection_ when objects are __loaded and manipulated__. This section presents additional information about _collection configuration and techniques_.


#### Working with Large Collections

The _default behavior_ of `relationship()` is to __fully load the collection of items in__, as according to the _loading strategy_ of the relationship. Additionally, the _Session_ __by default only knows__ how to _delete objects which are actually present within the session_. When a _parent instance_ is __marked for deletion and flushed__, the _Session_ __loads its full list of child items__ in so that they may either be _deleted_ as well, or have their _foreign key value set to null_; this is to __avoid constraint violations__. For _large collections of child items_, there are _several strategies to bypass full loading of child items_ both at _load time_ as well as _deletion time_.


##### Dynamic Relationship Loaders

> This loader is in the general case __not compatible__ with the `Asynchronous I/O (asyncio)` extension. It _can be used with some limitations_.

A `relationship()` which corresponds to a large collection __can be configured__ so that it _returns a legacy Query object_ when accessed, which __allows filtering of the relationship__ on criteria. The class is a special class _AppenderQuery_ returned in place of a collection when accessed. __Filtering criterion may be applied as well as limits and offsets__, either _explicitly_ or via _array slices_.

```
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    posts = relationship("Post", lazy="dynamic")


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    headline = Column(String(100))
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref=backref("posts", lazy="dynamic"))
```

```
jack = session.get(User, id)

# filter Jack's blog posts
posts = jack.posts.filter(Post.headline == "this is a post")

# apply array slices
posts = jack.posts[5:20]
```

The _dynamic relationship_ __supports limited write operations__, via the `AppenderQuery.append()` and `AppenderQuery.remove()` methods:

```
oldpost = jack.posts.filter(Post.headline == "old post").one()
jack.posts.remove(oldpost)

jack.posts.append(Post("new post"))
```

Since the _read side_ of the _dynamic relationship_ __always queries the database__, _changes to the underlying collection_ __will not be visible__ until the data has been _flushed_. However, as long as `"autoflush"` is enabled on the _Session_ in use, this will __occur automatically__ each time the collection is _about to emit a query_.

To place a _dynamic relationship on a backref_, use the `backref()` function in conjunction with `lazy="dynamic"`:

```
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    headline = Column(String(100))
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref=backref("posts", lazy="dynamic"))
```

Note that _eager/lazy loading_ options __cannot be used__ in conjunction _dynamic relationships_ at this time.

> ##### Warning
>
> The "dynamic" loader applies to collections only. It is not valid to use "dynamic" loaders with many-to-one, one-to-one, or uselist=False relationships. Newer versions of SQLAlchemy emit warnings or exceptions in these cases.


##### Setting Noload, RaiseLoad

A `"noload"` relationship __never loads from the database__, even when accessed. It is configured using `lazy="noload"`.

```
class ParentClass(Base):
    __tablename__ = "some_table"
    id = Column(Integer, primary_key=True)
    children = relationship("ChildClass", lazy="noload")


class ChildClass(Base):
    __tablename__ = "other_table"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("some_table.id"))
```

Above, the _children_ collection is __fully writeable__, and _changes to it_ will be __persisted to the database__ as well as __locally available for reading__ at the time they are added. However when instances of _ParentClass_ are __freshly loaded__ from the database, the __children collection stays empty__. The _noload strategy_ is also _available on a query_ option basis using the `noload()` loader option.

Alternatively, a `"raise"-loaded` relationship will _raise an InvalidRequestError_ where the attribute would __normally emit a lazy load__.

```
class RaiseLoadClass(Base):
    __tablename__ = "raiseload_table"
    id = Column(Integer, primary_key=True)
    children = relationship("LazyClass", lazy="raise")


class LazyClass(Base):
    __tablename__ = "lazy_table"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("raiseload_table.id"))
```

Above, _attribute access_ on the _children collection_ will __raise an exception__ if it was __not previously eagerloaded__. This includes _read access_ but for collections will _also affect write access_, as __collections can't be mutated without first loading them__. The rationale for this is to __ensure that an application is not emitting any unexpected lazy loads within a certain context__. Rather than having to read through SQL logs to determine that all necessary attributes were _eager loaded_, the `"raise" strategy` will _cause unloaded attributes to raise immediately if accessed_. The _raise strategy_ is also _available on a query_ option basis using the `raiseload()` loader option.


#### Customizing Collection Access

Mapping a _one-to-many_ or _many-to-many_ relationship results in a _collection of values accessible through an attribute_ on the parent instance. _By default_, this _collection_ is a `list`. _Collections_ are __not limited to lists__. _Sets_, _mutable sequences_ and _almost any other Python object that can act as a container_ can be used in place of the default list, by specifying the `relationship.collection_class` option on `relationship()`.


##### Dictionary Collections

A little _extra detail_ is needed when using a `dictionary` as a collection. This because _objects are always loaded from the database as lists_, and a __key-generation strategy__ must be available to _populate the dictionary correctly_. The `attribute_mapped_collection()` function is by far the _most common way_ to achieve a simple dictionary collection. It produces a _dictionary class_ that will _apply a particular attribute of the mapped class as a key_. Below we map an _Item_ class containing a dictionary of _Note_ items keyed to the _Note.keyword_ attribute.

```
class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    notes = relationship(
        "Note",
        collection_class=attribute_mapped_collection("keyword"),
        cascade="all, delete-orphan",
    )


class Note(Base):
    __tablename__ = "note"
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("item.id"), nullable=False)
    keyword = Column(String)
    text = Column(String)
    
    def __init__(self, keyword, text):
        self.keyword = keyword
        self.text = text
```

_Item.notes_ is then a dictionary:

```
item = Item()
item.notes["a"] = Note("a", "atext")
item.notes.items()
```

`attribute_mapped_collection()` will ensure that the _.keyword_ attribute of each _Note_ complies with the key in the dictionary. Such as, when assigning to _Item.notes_, the dictionary key we supply must match that of the actual _Note_ object:

```
item = Item()
item.notes = {
    "a": Note("a", "atext"),
    "b": Note("b", "btext"),
}
```

The attribute which `attribute_mapped_collection()` uses as a key __does not need to be mapped at all__! Using a regular Python `@property` __allows virtually any detail or combination of details__ about the object to be used as the key, as below when we establish it as a tuple of _Note.keyword_ and the first ten letters of the _Note.text_ field.

```
class ItemBackref(Base):
    __tablename__ = "item_backref"
    id = Column(Integer, primary_key=True)
    notes = relationship(
        "NoteBackref",
        collection_class=attribute_mapped_collection("note_key"),
        backref="item",
        cascade="all, delete-orphan",
    )


class NoteBackref(Base):
    __tablename__ = "note_backref"
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("item_backref.id"), nullable=False)
    keyword = Column(String)
    text = Column(String)
    
    @property
    def note_key(self):
        return (self.keyword, self.text[0:10])
    
    def __init__(self, keyword, text):
        self.keyword = keyword
        self.text = text
```

Above we added a _NoteBackref.item_ backref. Assigning to this __reverse relationship__, the _NoteBackref_ is added to the _ItemBackref.notes_ dictionary and the _key is generated_ for us __automatically__.

```
item = ItemBackref()
n1 = NoteBackref("a", "atext")
n1.item = item
item.notes
```

Other _built-in_ dictionary types include `column_mapped_collection()`, which is almost like `attribute_mapped_collection()` except given the _Column_ object __directly__.

```
class ItemColumned(Base):
    __tablename__ = "item_columned"
    id = Column(Integer, primary_key=True)
    notes = relationship(
        "Note",
        collection_class=column_mapped_collection(Note.__table__.c.keyword),
        cascade="all, delete-orphan",
    )
```

as well as `mapped_collection()` which is __passed any callable function__. Note that it's usually easier to use `attribute_mapped_collection()` along with a `@property` as mentioned earlier:

```
class ItemMapped(Base):
    __tablename__ = "item_mapped"
    id = Column(Integer, primary_key=True)
    notes = relationship(
        "Note",
        collection_class=mapped_collection(lambda note: note.text[0:10]),
        cascade="all, delete-orphan",
    )
```

_Dictionary mappings_ are often combined with the `"Association Proxy"` extension to __produce streamlined dictionary views__.


##### Dealing with Key Mutations and back-populating for Dictionary collections

When using `attribute_mapped_collection()`, the _"key"_ for the dictionary is _taken from an attribute_ on the target object. __Changes to this key are not tracked__. This means that the __key must be assigned towards when it is first used__, and if the key changes, the collection will not be mutated. A typical example where this might be an issue is when _relying upon backrefs to populate an attribute mapped collection_.

```
class A(Base):
    __tablename__ = "a"
    id = Column(Integer, primary_key=True)
    bs = relationship(
        "B",
        collection_class=attribute_mapped_collection("data"),
        back_populates="a",
    )


class B(Base):
    __tablename__ = "b"
    id = Column(Integer, primary_key=True)
    a_id = Column(ForeignKey("a.id"))
    data = Column(String)
    a = relationship("A", back_populates="bs")
```

Above, if we create a _B()_ that refers to a specific _A()_, the _back populates_ will then __add the B() to the A.bs collection__, however if the value of _B.data_ is __not set yet__, the key will be `None`:

```
a1 = A()
b1 = B(a=a1)
```

Setting _b1.data_ after the fact __does not update the collection__:

```
b1.data = "the key"
```

This can also be seen if one attempts to _set up B() in the constructor_. The _order of arguments changes the result_:

```
B(a=a1, data="the key")
B(data="the key", a=a1)
```

If _backrefs_ are being used in this way, __ensure that attributes are populated in the correct order__ using an `__init__` method.

An `event handler` such as the following may also be used to __track changes in the collection__ as well.
