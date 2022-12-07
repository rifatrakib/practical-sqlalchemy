from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import registry, declarative_base, polymorphic_union, relationship
from sqlalchemy.ext.declarative import ConcreteBase, AbstractConcreteBase

Base = declarative_base()
mapper_registry = registry()
metadata_obj = Base.metadata


class Employee(Base):
    __tablename__ = "employee"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))


class Manager(Employee):
    __tablename__ = "manager"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    manager_data = Column(String(50))
    
    __mapper_args__ = {
        "concrete": True,
    }


class Engineer(Employee):
    __tablename__ = "engineer"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    engineer_info = Column(String(50))
    
    __mapper_args__ = {
        "concrete": True,
    }


class ConcreteEmployee(ConcreteBase, Base):
    __tablename__ = "concrete_employee"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    
    __mapper_args__ = {
        "polymorphic_identity": "concrete_employee",
        "concrete": True,
    }


class ConcreteManager(ConcreteEmployee):
    __tablename__ = "concrete_manager"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    manager_data = Column(String(40))
    
    __mapper_args__ = {
        "polymorphic_identity": "concrete_manager",
        "concrete": True,
    }


class ConcreteEngineer(ConcreteEmployee):
    __tablename__ = "concrete_engineer"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    engineer_info = Column(String(40))
    
    __mapper_args__ = {
        "polymorphic_identity": "concrete_engineer",
        "concrete": True,
    }


class AbstractEmployee(Base):
    __abstract__ = True


class AbstractManager(AbstractEmployee):
    __tablename__ = "abstract_manager"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    manager_data = Column(String(40))


class AbstractEngineer(AbstractEmployee):
    __tablename__ = "abstract_engineer"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    engineer_info = Column(String(40))


class AbstractConcreteEmployee(AbstractConcreteBase, Base):
    pass


class AbstractConcreteManager(AbstractConcreteEmployee):
    __tablename__ = "abstract_concrete_manager"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    manager_data = Column(String(40))
    
    __mapper_args__ = {
        "polymorphic_identity": "abstract_concrete_manager",
        "concrete": True,
    }


class AbstractConcreteEngineer(AbstractConcreteEmployee):
    __tablename__ = "abstract_concrete_engineer"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    engineer_info = Column(String(40))
    
    __mapper_args__ = {
        "polymorphic_identity": "abstract_concrete_engineer",
        "concrete": True,
    }


employees_table = Table(
    "semi_classic_employee",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
)

managers_table = Table(
    "semi_classic_manager",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("manager_data", String(50)),
)

engineers_table = Table(
    "semi_classic_engineer",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("engineer_info", String(50)),
)

pjoin = polymorphic_union(
    {
        "employee": employees_table,
        "manager": managers_table,
        "engineer": engineers_table,
    },
    "type",
    "pjoin",
)


class PjoinEmployee(Base):
    __table__ = employees_table
    
    __mapper_args__ = {
        "polymorphic_on": pjoin.c.type,
        "with_polymorphic": ("*", pjoin),
        "polymorphic_identity": "employee",
    }


class PjoinEngineer(Employee):
    __table__ = engineers_table
    __mapper_args__ = {
        "polymorphic_identity": "engineer",
        "concrete": True,
    }


class PjoinManager(Employee):
    __table__ = managers_table
    __mapper_args__ = {
        "polymorphic_identity": "manager",
        "concrete": True,
    }


class ClassicalEmployee:
    def __init__(self, **kw):
        for k in kw:
            setattr(self, k, kw[k])


class ClassicalManager(ClassicalEmployee):
    pass


class ClassicalEngineer(ClassicalEmployee):
    pass


employee_mapper = mapper_registry.map_imperatively(
    ClassicalEmployee,
    pjoin,
    with_polymorphic=("*", pjoin),
    polymorphic_on=pjoin.c.type,
)

manager_mapper = mapper_registry.map_imperatively(
    ClassicalManager,
    managers_table,
    inherits=employee_mapper,
    concrete=True,
    polymorphic_identity="manager",
)

engineer_mapper = mapper_registry.map_imperatively(
    ClassicalEngineer,
    engineers_table,
    inherits=employee_mapper,
    concrete=True,
    polymorphic_identity="engineer",
)

pjoin = polymorphic_union(
    {
        "manager": managers_table,
        "engineer": engineers_table,
    },
    "type",
    "pjoin",
)


class SelectableEmployee(Base):
    __table__ = pjoin
    
    __mapper_args__ = {
        "polymorphic_on": pjoin.c.type,
        "with_polymorphic": "*",
        "polymorphic_identity": "employee",
    }


class SelectableEngineer(SelectableEmployee):
    __table__ = engineers_table
    
    __mapper_args__ = {
        "polymorphic_identity": "engineer",
        "concrete": True,
    }


class SelectableManager(SelectableEmployee):
    __table__ = managers_table
    
    __mapper_args__ = {
        "polymorphic_identity": "manager",
        "concrete": True,
    }


class InheritenceCompany(Base):
    __tablename__ = "inheritence_company"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    employees = relationship("InheritenceEmployee")


class InheritenceEmployee(ConcreteBase, Base):
    __tablename__ = "inheritence_employee"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    company_id = Column(ForeignKey("inheritence_company.id"))
    
    __mapper_args__ = {
        "polymorphic_identity": "inheritence_employee",
        "concrete": True,
    }


class InheritenceManager(Employee):
    __tablename__ = "inheritence_manager"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    manager_data = Column(String(40))
    company_id = Column(ForeignKey("inheritence_company.id"))
    
    __mapper_args__ = {
        "polymorphic_identity": "inheritence_manager",
        "concrete": True,
    }


class InheritenceEngineer(Employee):
    __tablename__ = "inheritence_engineer"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    engineer_info = Column(String(40))
    company_id = Column(ForeignKey("inheritence_company.id"))
    
    __mapper_args__ = {
        "polymorphic_identity": "inheritence_engineer",
        "concrete": True,
    }


class BackCompany(Base):
    __tablename__ = "back_company"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    employees = relationship("BackEmployee", back_populates="company")


class BackEmployee(ConcreteBase, Base):
    __tablename__ = "back_employee"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    company_id = Column(ForeignKey("back_company.id"))
    company = relationship("BackCompany", back_populates="employees")
    
    __mapper_args__ = {
        "polymorphic_identity": "back_employee",
        "concrete": True,
    }


class BackManager(BackEmployee):
    __tablename__ = "back_manager"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    manager_data = Column(String(40))
    company_id = Column(ForeignKey("back_company.id"))
    company = relationship("BackCompany", back_populates="employees")
    
    __mapper_args__ = {
        "polymorphic_identity": "back_manager",
        "concrete": True,
    }


class BackEngineer(BackEmployee):
    __tablename__ = "back_engineer"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    engineer_info = Column(String(40))
    company_id = Column(ForeignKey("back_company.id"))
    company = relationship("BackCompany", back_populates="employees")
    
    __mapper_args__ = {
        "polymorphic_identity": "back_engineer",
        "concrete": True,
    }
