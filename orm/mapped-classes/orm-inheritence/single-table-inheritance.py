from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declared_attr, declarative_base, relationship

Base = declarative_base()


class Company(Base):
    __tablename__ = "company"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    employees = relationship("Employee", back_populates="company")


class Employee(Base):
    __tablename__ = "employee"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(50))
    
    company_id = Column(ForeignKey("company.id"))
    company = relationship("Company", back_populates="employees")
    
    __mapper_args__ = {
        "polymorphic_identity": "employee",
        "polymorphic_on": type,
    }


class Manager(Employee):
    __mapper_args__ = {
        "polymorphic_identity": "manager",
    }
    
    @declared_attr
    def start_date(cls):
        """Start date column, if not present already"""
        return Employee.__table__.c.get("start_date", Column(DateTime))


class Engineer(Employee):
    __mapper_args__ = {
        "polymorphic_identity": "engineer",
    }
    
    @declared_attr
    def start_date(cls):
        """Start date column, if not present already"""
        return Employee.__table__.c.get("start_date", Column(DateTime))
