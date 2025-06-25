
"""
Proper database layer implementation with SQLAlchemy for academic writing system.
"""

from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    preferences = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    project_type = Column(String, nullable=False)
    style = Column(String, default='Standard')
    discipline = Column(String)
    status = Column(String, default='created')
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="projects")
    sections = relationship("Section", back_populates="project", cascade="all, delete-orphan")
    versions = relationship("ProjectVersion", back_populates="project", cascade="all, delete-orphan")

class Section(Base):
    __tablename__ = 'sections'
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey('projects.id'), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, default='')
    order_index = Column(Integer, nullable=False)
    metadata = Column(JSON, default={})
    fileverse_pad_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="sections")

class ProjectVersion(Base):
    __tablename__ = 'project_versions'
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey('projects.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    content_snapshot = Column(JSON, nullable=False)
    change_description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="versions")

class DatabaseManager:
    """Thread-safe database manager with connection pooling."""
    
    def __init__(self, database_url: str = None):
        if database_url is None:
            database_url = os.getenv('DATABASE_URL', 'sqlite:///data/academic_writing.db')
        
        self.engine = create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=False
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get database session with proper cleanup."""
        return self.SessionLocal()
    
    def health_check(self) -> bool:
        """Check database connectivity."""
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
                return True
        except Exception:
            return False

# Global database instance
db_manager = DatabaseManager()
