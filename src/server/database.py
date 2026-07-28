import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, "workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(WORKSPACE_DIR, 'logfilter.db')}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Issue(Base):
    __tablename__ = "issues"
    id = Column(String, primary_key=True, index=True) # e.g. ISSUE-8492
    title = Column(String)
    component = Column(String)
    status = Column(String, default="Open")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def init_db():
    Base.metadata.create_all(bind=engine)
