from sqlalchemy import Column, Integer, String, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class EmailAddressWithProperty(Base):
    __tablename__ = "email_address"
    
    id = Column(Integer, primary_key=True)
    # name the attribute with an underscore, different from the column name
    _email = Column("email", String)
    
    # then create an ".email" attribute, to get/set "._email"
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, email):
        self._email = email


class EmailAddressHybridExtension(Base):
    __tablename__ = "email_address_hybrid"
    
    id = Column(Integer, primary_key=True)
    _email = Column("email", String)
    
    @hybrid_property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, email):
        self._email = email


class EmailAddressPropertyExpression(Base):
    __tablename__ = "email_address_expression"
    
    id = Column(Integer, primary_key=True)
    _email = Column("email", String)
    
    @hybrid_property
    def email(self):
        """Return the value of _email up until the last twelve characters."""
        return self._email[:-12]
    
    @email.setter
    def email(self, email):
        """Set the value of _email, tacking on the twelve character value @example.com."""
        self._email = f"{email}@example.com"
    
    @email.expression
    def email(cls):
        """Produce a SQL expression that represents the value
        of the _email column, minus the last twelve characters."""
        return func.substr(cls._email, 0, func.length(cls._email) - 12)
