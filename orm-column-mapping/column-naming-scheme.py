from sqlalchemy import Column, Integer, String, Table, event, create_engine
from sqlalchemy.orm import declarative_base

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
Base = declarative_base()


@event.listens_for(Base.metadata, "column_reflect")
def column_reflect(inspector, table, column_info):
    # set column.key = "attr_<lower_case_name>"
    column_info["key"] = f"attr_{column_info['name'].lower()}"


class UserTable(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String)


Base.metadata.create_all(engine)


class User(Base):
    __table__ = Table(
        "user",
        Base.metadata,
        autoload_with=engine,
    )
