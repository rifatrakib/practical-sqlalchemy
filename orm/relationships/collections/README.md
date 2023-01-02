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


#### Custom Collection Implementations

You can use your own types for collections as well. In simple cases, _inheriting_ from `list` or `set`, _adding custom behavior_, is all that's needed. In other cases, _special decorators_ are needed to tell SQLAlchemy __more detail about how the collection operates__.

> ###### Do I need a custom collection implementation?
>
> In most cases not at all! The most common use cases for a "custom" collection is one that _validates or marshals incoming values into a new form_, such as a string that becomes a class instance, or one which goes a step beyond and _represents the data internally in some fashion_, presenting a "view" of that data on the outside of a different form.
>
> For the first use case, the `validates()` decorator is by far the _simplest way to intercept incoming values_ in all cases for the purposes of __validation and simple marshaling__.
>
> For the second use case, the _Association Proxy extension_ is a _well-tested_, _widely used_ system that provides a __read/write "view" of a collection__ in terms of some attribute present on the target object. As the _target attribute_ can be a `@property` that returns virtually _anything_, a _wide array of "alternative" views_ of a collection can be constructed with just a few functions. This approach leaves the __underlying mapped collection unaffected and avoids the need to carefully tailor collection behavior on a method-by-method basis__.
>
> _Customized collections_ are useful when the collection needs to have _special behaviors upon access or mutation operations_ that __can't otherwise be modeled externally__ to the collection. They can of course be __combined__ with the _above two approaches_.

Collections in SQLAlchemy are _transparently instrumented_. `Instrumentation` means that _normal operations on the collection are tracked and result in changes being written to the database at flush time_. Additionally, collection operations __can fire events__ which indicate some secondary operation must take place. Examples of a secondary operation include saving the child item in the parent's _Session_ (i.e. the _save-update cascade_), as well as _synchronizing_ the state of a `bi-directional relationship` (i.e. a `backref()`).

The collections package understands the _basic interface of lists, sets and dicts_ and will __automatically apply instrumentation__ to those built-in types and their subclasses. _Object-derived types_ that implement a basic collection interface are __detected and instrumented via duck-typing__.

```
class ListLike(object):
    def __init__(self):
        self.data = []
    
    def append(self, item):
        self.data.append(item)
    
    def remove(self, item):
        self.data.remove(item)
    
    def extend(self, items):
        self.data.extend(items)
    
    def __iter__(self):
        return iter(self.data)
    
    def foo(self):
        return "foo"
```

`append`, `remove`, and `extend` are known _list-like_ methods, and will be __instrumented automatically__. `__iter__` is __not__ a _mutator method_ and _won't be instrumented_, and foo won't be either.

_Duck-typing_ (i.e. guesswork) __isn't rock-solid__, of course, so you can be _explicit_ about the interface you are implementing by providing an `__emulates__` class attribute.

```
class SetLike(object):
    __emulates__ = set
    
    def __init__(self):
        self.data = set()
    
    def append(self, item):
        self.data.add(item)
    
    def remove(self, item):
        self.data.remove(item)
    
    def __iter__(self):
        return iter(self.data)
```

This class looks _list-like_ because of `append`, but `__emulates__` __forces it to set-like__. `remove` is known to be part of the _set interface_ and __will be instrumented__.

But this class __won't work__ quite yet: a __little glue is needed to adapt it__ for use by _SQLAlchemy_. The ORM _needs to know_ which methods to use to _append_, _remove_ and _iterate_ over members of the collection. When using a type like _list_ or _set_, the __appropriate methods are well-known and used automatically__ when present. This _set-like_ class __does not provide the expected add method__, so we __must supply an explicit mapping__ for the ORM _via a decorator_.


##### Annotating Custom Collections via Decorators

_Decorators_ can be used to __tag the individual methods__ the ORM needs to _manage collections_. Use them when your class __doesn't quite meet the regular interface__ for its _container type_, or when you otherwise would like to use a _different method to get the job done_.

```
class SetLike(object):
    __emulates__ = set
    
    def __init__(self):
        self.data = set()
    
    @collection.appender
    def append(self, item):
        self.data.add(item)
    
    def remove(self, item):
        self.data.remove(item)
    
    def __iter__(self):
        return iter(self.data)
```

And that's all that's needed to complete the example. SQLAlchemy will _add instances via the append method_. `remove` and `__iter__` are the _default methods_ for sets and will be used for _removing_ and _iteration_. __Default methods can be changed as well__.

There is __no requirement__ to be _list-_, or _set-like_ at all. __Collection classes can be any shape__, so long as they have the `append`, `remove` and `iterate` interface marked for SQLAlchemy's use. _Append_ and _remove_ methods will be __called with a mapped entity as the single argument__, and _iterator_ methods are called with __no arguments__ and __must return an iterator__.


##### Custom Dictionary-Based Collections

The _MappedCollection_ class can be used as a _base class for your custom types_ or as a _mix-in_ to __quickly add dict collection support to other classes__. It uses a _keying function_ to delegate to `__setitem__` and `__delitem__`.

```
class NodeMap(MappedCollection):
    """Holds 'Node' objects, keyed by the 'name' attribute with insert order maintained."""
    
    def __init__(self, *args, **kw):
        MappedCollection.__init__(self, keyfunc=lambda node: node.name)
        OrderedDict.__init__(self, *args, **kw)
```

When subclassing _MappedCollection_, _user-defined_ versions of `__setitem__()` or `__delitem__()` should be __decorated__ with `collection.internally_instrumented()`, if they __call down to those same methods__ on _MappedCollection_. This because the methods on _MappedCollection_ are __already instrumented__ - calling them from within an _already instrumented_ call can __cause events to be fired off repeatedly__, or __inappropriately__, leading to `internal state corruption` in rare cases.

The ORM understands the _dict interface_ just like _lists_ and _sets_, and will __automatically instrument all dict-like methods__ if you choose to _subclass dict or provide dict-like collection behavior_ in a duck-typed class. You __must decorate appender and remover methods__, however- there are _no compatible methods in the basic dictionary interface_ for SQLAlchemy to use by default. Iteration will go through `itervalues()` _unless otherwise decorated_.


##### Instrumentation and Custom Types

Many _custom types_ and _existing library classes_ can be used as a `entity collection type` __as-is without further ado__. However, it is important to note that the _instrumentation_ process will _modify the type_, _adding decorators_ around methods __automatically__.

The _decorations_ are __lightweight and no-op outside of relationships__, but they do __add unneeded overhead when triggered elsewhere__. When using a library class as a collection, it can be good practice to use the _"trivial subclass"_ trick to _restrict the decorations_ to just your usage in relationships.

```
class MyAwesomeList(some.great.library.AwesomeList):
    pass


# ... relationship(..., collection_class=MyAwesomeList)
```

The ORM uses this approach for _built-ins_, __quietly substituting a trivial subclass__ when a `list`, `set` or `dict` is _used directly_.
