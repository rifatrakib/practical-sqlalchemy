## SQL Expressions as Mapped Attributes

_Attributes_ on a mapped class __can be linked__ to `SQL expressions`, which can be used in queries.


#### Using a Hybrid

The _easiest_ and _most flexible_ way to __link relatively simple SQL expressions__ to a class is to use a so-called `"hybrid attribute"`, described in the section `Hybrid Attributes`. The _hybrid_ provides for an _expression_ that works at both the _Python level_ as well as at the _SQL expression level_. For example, below we map a class `User`, containing attributes _firstname_ and _lastname_, and _include a hybrid_ that will provide for us the _fullname_, which is the `string concatenation` of the two.

```
class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    
    @hybrid_property
    def fullname(self):
        return f"{self.firstname} {self.lastname}"
```

Above, the _fullname_ attribute is __interpreted at both the instance and class level__, so that it is available from an instance.

```
some_user = session.query(User).first()
print(some_user.fullname)
```

as well as usable within queries:

```
some_user = session.query(User).filter(User.fullname == "John Smith").first()
```

The _string concatenation_ example is a simple one, where the _Python expression_ __can be dual purposed__ at the _instance and class level_. Often, the _SQL expression_ __must be distinguished__ from the _Python expression_, which can be achieved using `hybrid_property.expression()`. Below we illustrate the case where a __conditional needs to be present inside the hybrid__, using the `if statement` in _Python_ and the `case()` construct for _SQL expressions_.
