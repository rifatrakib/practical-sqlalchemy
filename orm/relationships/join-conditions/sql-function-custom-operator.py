from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, func
from sqlalchemy.orm import declarative_base, foreign, relationship

Base = declarative_base()


class Polygon(Base):
    __tablename__ = "polygon"
    
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry("POLYGON", srid=4326))
    points = relationship(
        "Point", viewonly=True,
        primaryjoin="func.ST_Contains(foreign(Polygon.geom), Point.geom).as_comparison(1, 2)",
    )


class Point(Base):
    __tablename__ = "point"
    
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry("POINT", srid=4326))
