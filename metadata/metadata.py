from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, text, create_engine
from sqlalchemy.orm import registry, relationship

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)


def core_based_approach():
    metadata_obj = MetaData()
    user_table = Table(
        "user_account", metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("name", String(30)),
        Column("fullname", String),
    )
    
    print(user_table.c.name)
    print(user_table.c.keys())
    
    address_table = Table(
        "address", metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("user_id", ForeignKey("user_account.id"), nullable=False),
        Column("email_address", String, nullable=False)
    )
    
    metadata_obj.create_all(engine)


def orm_based_approach():
    mapped_registry = registry()
    print(mapped_registry.metadata)
    Base = mapped_registry.generate_base()
    
    class User(Base):
        __tablename__ = "user_account"
        
        id = Column(Integer, primary_key=True)
        name = Column(String(30))
        fullname = Column(String)
        
        addresses = relationship("Address", back_populates="user")
        
        def __repr__(self):
            return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"
    
    class Address(Base):
        __tablename__ = "address"
        
        id = Column(Integer, primary_key=True)
        email_address = Column(String, nullable=False)
        user_id = Column(Integer, ForeignKey("user_account.id"))
        
        user = relationship("User", back_populates="addresses")
        
        def __repr__(self):
            return f"Address(id={self.id!r}, email_address={self.email_address!r})"
    
    print(User.__table__)
    print(Address.__table__)
    
    # emit CREATE statements given ORM registry
    mapped_registry.metadata.create_all(engine)
    
    # the identical MetaData object is also present on the declarative base
    Base.metadata.create_all(engine)


def hybrid_approach():
    mapper_registry = registry()
    Base = mapper_registry.generate_base()
    
    metadata_obj = MetaData()
    user_table = Table(
        "user_account", metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("name", String(30)),
        Column("fullname", String),
    )
    
    print(user_table.c.name)
    print(user_table.c.keys())
    
    address_table = Table(
        "address", metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("user_id", ForeignKey("user_account.id"), nullable=False),
        Column("email_address", String, nullable=False)
    )
    
    class User(Base):
        __table__ = user_table
        
        addresses = relationship("Address", back_populates="user")
        
        def __repr__(self):
            return f"User({self.name!r}, {self.fullname!r})"
    
    class Address(Base):
        __table__ = address_table
        
        user = relationship("User", back_populates="addresses")
        
        def __repr__(self):
            return f"Address({self.email_address!r})"


def reflection():
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE table_name (x int, y int)"))
        conn.execute(
            text("INSERT INTO table_name (x, y) VALUES (:x, :y)"),
            [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
        )
        conn.commit()
    
    metadata_obj = MetaData()
    some_table = Table("table_name", metadata_obj, autoload_with=engine)
    print(some_table)
