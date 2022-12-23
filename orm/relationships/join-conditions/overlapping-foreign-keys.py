from sqlalchemy import (
    Column, ForeignKey, ForeignKeyConstraint,
    Integer, PrimaryKeyConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Magazine(Base):
    __tablename__ = "magazine"
    id = Column(Integer, primary_key=True)


class Article(Base):
    __tablename__ = "article"
    
    article_id = Column(Integer)
    magazine_id = Column(ForeignKey("magazine.id"))
    writer_id = Column()
    
    magazine = relationship("Magazine")
    writer = relationship(
        "Writer",
        primaryjoin="and_(Writer.id == foreign(Article.writer_id), "
        "Writer.magazine_id == Article.magazine_id",
    )
    
    __table_args__ = (
        PrimaryKeyConstraint("article_id", "magazine_id"),
    )


class Writer(Base):
    __tablename__ = "writer"
    
    id = Column(Integer, primary_key=True)
    magazine_id = Column(ForeignKey("magazine.id"), primary_key=True)
    magazine = relationship("Magazine")
