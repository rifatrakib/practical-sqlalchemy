from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Employee(Base):
    __tablename__ = "employee"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(50))
    
    company_id = Column(ForeignKey("company.id"))
    company_employees = relationship("Company", back_populates="employees")
    
    __mapper_args__ = {
        "polymorphic_identity": "employee",
        "polymorphic_on": type,
    }


class Engineer(Base):
    __tablename__ = "engineer"
    
    id = Column(Integer, ForeignKey("employee.id"), primary_key=True)
    engineer_name = Column(String(30))
    
    company_id = Column(ForeignKey("company.id"))
    company_employees = relationship("Company", back_populates="employees")
    company_engineers = relationship("Company", back_populates="engineers")
    
    __mapper_args__ = {
        "polymorphic_identity": "engineer",
    }


class Manager(Base):
    __tablename__ = "manager"
    
    id = Column(Integer, ForeignKey("employee.id"), primary_key=True)
    manager_name = Column(String(30))
    
    company_id = Column(ForeignKey("company.id"))
    company_employees = relationship("Company", back_populates="employees")
    company_managers = relationship("Company", back_populates="managers")
    
    __mapper_args__ = {
        "polymorphic_identity": "manager",
    }


class Company(Base):
    __tablename__ = "company"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    employees = relationship("Employee", back_populates="company_employees")
    managers = relationship("Manager", back_populates="company_managers")
    engineers = relationship("Manager", back_populates="company_engineers")
