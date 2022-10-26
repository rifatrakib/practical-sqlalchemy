from sqlalchemy.orm import registry, declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String

reg = registry()
Base = reg.generate_base()

Base = declarative_base()



