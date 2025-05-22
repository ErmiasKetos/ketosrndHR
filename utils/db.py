import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Database URL (fallback to SQLite file if not provided)
DB_URL = os.getenv("DATABASE_URL", "sqlite:///ketos_resumes.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    name = Column(String)
    password = Column(String)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    criteria = Column(JSON)
    threshold = Column(Float, default=0.0)
    candidates = relationship("Candidate", back_populates="job")

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    score = Column(Float)
    summary = Column(Text)
    status = Column(String, default="Pending")
    raw_data = Column(JSON)
    job = relationship("Job", back_populates="candidates")

# Database utility functions

def get_db():
    """
    Provide a transactional scoped database session.
    """
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_job(db, job_id=None):
    """
    Fetch the most recent job if no ID is specified.
    """
    return db.query(Job).order_by(Job.id.desc()).first()

