from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Parent(Base):
    __tablename__ = "parent_table"
    id = Column(Integer, primary_key=True)
    children = relationship(
        "Child", back_populates="parent",
        order_by="desc(Child.id)",
        primaryjoin="Parent.id == Child.parent_id",
    )


class Child(Base):
    __tablename__ = "child_table"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("parent_table.id"))
    parent = relationship("Parent", back_populates="children")


keyword_author = Table(
    "keyword_author_table",
    Base.metadata,
    Column("author_id", Integer, ForeignKey("authors_table.id")),
    Column("keyword_id", Integer, ForeignKey("keywords_table.id")),
)


class Author(Base):
    __tablename__ = "authors_table"
    id = Column(Integer, primary_key=True)
    keywords = relationship("Keyword", secondary="keyword_author_table")
