from sqlalchemy.util import OrderedDict
from sqlalchemy.orm.collections import collection, MappedCollection


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


"""
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
"""


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


class MyList(list):
    @collection.remover
    def zark(self, item):
        # do something special...
        pass
    
    @collection.iterator
    def hey_use_this_instead_for_iteration(self):
        pass


class NodeMap(MappedCollection):
    """Holds 'Node' objects, keyed by the 'name' attribute with insert order maintained."""
    
    def __init__(self, *args, **kw):
        MappedCollection.__init__(self, keyfunc=lambda node: node.name)
        OrderedDict.__init__(self, *args, **kw)


class MyMappedCollection(MappedCollection):
    """Use @internally_instrumented when your methods
    call down to already-instrumented methods.
    """
    
    @collection.internally_instrumented
    def __setitem__(self, key, value, _sa_initiator=None):
        # do something with key, value
        super(MyMappedCollection, self).__setitem__(key, value, _sa_initiator)
    
    @collection.internally_instrumented
    def __delitem__(self, key, _sa_initiator=None):
        # do something with key
        super(MyMappedCollection, self).__delitem__(key, _sa_initiator)
