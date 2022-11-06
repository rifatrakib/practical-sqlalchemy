from sqlalchemy import Column, Integer, String, Table, MetaData, PrimaryKeyConstraint
from sqlalchemy.orm import declared_attr, registry, declarative_base

Base = declarative_base()


class AfterUserClass(Base):
    __tablename__ = "after_user"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    firstname = Column(String(50))
    lastname = Column(String(50))
    
    @classmethod
    def __declare_last__(cls):
        print("configured already")


class BeforeUserClass(Base):
    __tablename__ = "before_user"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    firstname = Column(String(50))
    lastname = Column(String(50))
    
    @classmethod
    def __declare_first__(cls):
        print("initializing configuration")


reg = registry()


class BaseOne:
    metadata = MetaData()


class BaseTwo:
    metadata = MetaData()


@reg.mapped
class ClassOne:
    __tablename__ = "t1"  # will use reg.metadata
    
    id = Column(Integer, primary_key=True)


@reg.mapped
class ClassTwo(BaseOne):
    __tablename__ = "t2"  # will use BaseOne.metadata
    
    id = Column(Integer, primary_key=True)


@reg.mapped
class ClassThree(BaseTwo):
    __tablename__ = "t3"  # will use BaseTwo.metadata
    
    id = Column(Integer, primary_key=True)


class AbstractUserClass(Base):
    __astract__ = True
    __tablename__ = "abstract_user"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    firstname = Column(String(50))
    lastname = Column(String(50))
    
    def helpful_abstract_method(self):
        print("inside abstract method")
    
    @declared_attr
    def __mapper_args__(cls):
        return {
            "exclude_properties": [
                column.key for column in cls.__table__.c
                if column.info.get("exclude", False)
            ]
        }


class MappedUserClass(AbstractUserClass):
    pass


class DefaultBase(Base):
    __abstract__ = True
    metadata = MetaData()


class OtherBase(Base):
    __abstract__ = True
    metadata = MetaData()


class CustomMixin(object):
    @classmethod
    def __table_cls__(cls, name, metadata_obj, *args, **kwargs):
        return Table(f"custom_{name}", metadata_obj, *args, **kwargs)


class AutoTable(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__
    
    @classmethod
    def __table_cls__(cls, *args, **kwargs):
        for obj in args[1:]:
            if (isinstance(obj, Column) and obj.primary_key) or isinstance(obj, PrimaryKeyConstraint):
                return Table(*args, **kwargs)
        return None


class Person(AutoTable, Base):
    id = Column(Integer, primary_key=True)


class Employee(Person):
    employee_name = Column(String)
