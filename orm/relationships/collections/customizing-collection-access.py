from sqlalchemy import Column, ForeignKey, Integer, String, event
from sqlalchemy.orm import declarative_base, relationship, attributes
from sqlalchemy.orm.collections import (
    attribute_mapped_collection, column_mapped_collection, mapped_collection
)

Base = declarative_base()


class ParentClass(Base):
    __tablename__ = "some_table"
    id = Column(Integer, primary_key=True)
    children = relationship("ChildClass", lazy="noload", collection_class=set)


class ChildClass(Base):
    __tablename__ = "other_table"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("some_table.id"))


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


class ItemColumned(Base):
    __tablename__ = "item_columned"
    id = Column(Integer, primary_key=True)
    notes = relationship(
        "Note",
        collection_class=column_mapped_collection(Note.__table__.c.keyword),
        cascade="all, delete-orphan",
    )


class ItemMapped(Base):
    __tablename__ = "item_mapped"
    id = Column(Integer, primary_key=True)
    notes = relationship(
        "Note",
        collection_class=mapped_collection(lambda note: note.text[0:10]),
        cascade="all, delete-orphan",
    )


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


@event.listens_for(B.data, "set")
def set_item(obj, value, previous, initiator):
    if obj.a is not None:
        previous = None if previous == attributes.NO_VALUE else previous
        obj.a.bs[value] = obj
        obj.a.bs.pop(previous)
