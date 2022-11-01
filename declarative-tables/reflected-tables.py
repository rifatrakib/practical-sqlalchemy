from sqlalchemy import Column, Integer, String, Table, create_engine
from sqlalchemy.orm import declarative_base

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
Base = declarative_base()
