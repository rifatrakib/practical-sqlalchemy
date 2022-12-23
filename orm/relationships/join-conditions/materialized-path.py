from sqlalchemy import cast, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import foreign, remote, relationship

Base = declarative_base()


class Element(Base):
    __tablename__ = "element"
    path = Column(String, primary_key=True)
    descendants = relationship(
        "Element",
        primaryjoin=remote(foreign(path)).like(path.concat("/%")),
        viewonly=True,
        order_by=path,
    )
