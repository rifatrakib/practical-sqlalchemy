from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

import uuid

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
Base = declarative_base()
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    version_uuid = Column(String(32), nullable=False)
    name = Column(String(50), nullable=False)
    
    __mapper_args__ = {"version_id_col": version_uuid, "version_id_generator": False}


Base.metadata.create_all(engine)

u1 = User(name="u1", version_uuid=uuid.uuid4())
session.add(u1)
session.commit()

u1.name = "u2"
u1.version_uuid = uuid.uuid4()
session.commit()

# will leave version_uuid unchanged
u1.name = "u3"
session.commit()
