from sqlalchemy import Column, ForeignKeyConstraint, Integer, String
from sqlalchemy.orm import backref, declarative_base, relationship

Base = declarative_base()


class Folder(Base):
    __tablename__ = "folder"
    __table_args__ = (
        ForeignKeyConstraint(
            ["account_id", "parent_id"],
            ["folder.account_id", "folder.folder_id"],
        ),
    )
    
    account_id = Column(Integer, primary_key=True)
    folder_id = Column(Integer, primary_key=True)
    parent_id = Column(Integer)
    name = Column(String)
    
    parent_folder = relationship(
        "Folder", backref="child_folders",
        remote_side=[account_id, folder_id],
    )
