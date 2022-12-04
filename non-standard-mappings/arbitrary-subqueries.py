from sqlalchemy import Column, ForeignKey, Integer, String, Table, select, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

customers = Table(
    "customers",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
)

orders = Table(
    "orders",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("customer_id", Integer, ForeignKey("customers.id")),
    Column("price", Integer),
)

subq = (
    select(
        func.count(orders.c.id).label("order_count"),
        func.max(orders.c.price).label("highest_order"),
        orders.c.customer_id,
    ).group_by(orders.c.customer_id).subquery()
)

customer_select = (
    select(customers, subq).
    join_from(customers, subq, customers.c.id == subq.c.customer_id).
    subquery()
)


class Customer(Base):
    __table__ = customer_select
