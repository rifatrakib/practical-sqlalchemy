from sqlalchemy import Column, ForeignKey, Integer, String, Table, MetaData
from sqlalchemy.orm import declarative_base, column_property

metadata_obj = MetaData()
Base = declarative_base()


class BaseUser(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    name = column_property(Column(String(50)), active_history=True)


user_table = Table(
    "user",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String),
)

address_table = Table(
    "address",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("email_address", String),
)


class User(Base):
    __table__ = user_table.join(address_table)
    
    # assign "user.id", "address.user_id" to the "id" attribute
    id = column_property(user_table.c.id, address_table.c.user_id)
    address_id = address_table.c.id


class ConcatUser(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    fullname = column_property(firstname + " " + lastname)
