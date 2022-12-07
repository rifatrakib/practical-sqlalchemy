from sqlalchemy import (
    Column, ForeignKey, Integer, String, Table,
    select, func, inspect, and_,
)
from sqlalchemy.orm import column_property, registry
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
reg = registry()


class SimpleUser(Base):
    __tablename__ = "simple_user"
    
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    fullname = column_property(firstname + " " + lastname)


class Address(Base):
    __tablename__ = "address"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    address_count = column_property(
        select(func.count(Address.id)).
        where(Address.user_id == id).
        correlate_except(Address).
        scalar_subquery()
    )


class MappedAddress(Base):
    __tablename__ = "address"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("mapped_user.id"))


@reg.mapped
class MappedUser:
    __tablename__ = "mapped_user"
    
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))


inspect(MappedUser).add_property(
    "address_count", column_property(
        select(func.count(MappedAddress.id)).
        where(MappedAddress.user_id == MappedUser.id).
        scalar_subquery()
    )
)

books = Table(
    "books",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
)

authors = Table(
    "authors",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
)

book_authors = Table(
    "book_authors",
    Base.metadata,
    Column("author_id", Integer, ForeignKey("authors.id")),
    Column("book_id", Integer, ForeignKey("books.id")),
)


class Author(Base):
    __table__ = authors
    
    book_count = column_property(
        select(func.count(books.c.id)).
        where(
            and_(
                book_authors.c.author_id == authors.c.id,
                book_authors.c.book_id == books.c.id,
            )
        ).scalar_subquery()
    )


class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    extension = Column(String(8))
    filename = column_property(name + "." + extension)
    path = column_property("C:/" + filename.expression)
