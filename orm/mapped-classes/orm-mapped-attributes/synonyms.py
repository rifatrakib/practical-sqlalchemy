from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.orm import declarative_base, registry, synonym
from sqlalchemy.ext.declarative import synonym_for

Base = declarative_base()
mapper = registry()


class JobStatus(Base):
    __tablename__ = "my_table"
    
    id = Column(Integer, primary_key=True)
    job_status = Column(String(50))
    
    status = synonym("job_status")


class StatusProperty(Base):
    __tablename__ = "status_property"
    
    id = Column(Integer, primary_key=True)
    status = Column(String(50))
    
    @property
    def job_status(self):
        return f"Status: {self.status}"
    
    job_status = synonym("status", descriptor=job_status)


class DeclarativeStatus(Base):
    __tablename__ = "declarative_status"
    
    id = Column(Integer, primary_key=True)
    status = Column(String(50))
    
    @synonym_for("status")
    @property
    def job_status(self):
        return f"Status: {self.status}"


mapped_table = Table(
    "mapped_table",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("job_status", String(50))
)


class MappedTable:
    @property
    def _job_status_descriptor(self):
        return f"Status: {self._job_status}"


mapper.map_imperatively(
    MappedTable, mapped_table,
    properties={
        "job_status": synonym(
            "_job_status", map_column=True,
            descriptor=MappedTable._job_status_descriptor,
        )
    }
)
