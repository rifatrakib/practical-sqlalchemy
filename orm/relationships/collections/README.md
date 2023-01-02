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
