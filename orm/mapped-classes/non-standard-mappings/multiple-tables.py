from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table, join
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property

metadata_obj = MetaData()
Base = declarative_base()

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

user_address_join = join(user_table, address_table)


class AddressUser(Base):
    __table__ = user_address_join
    
    id = column_property(user_table.c.id, address_table.c.id)
    address_id = address_table.c.id
