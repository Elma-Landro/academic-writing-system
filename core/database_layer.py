
"""
Professional database layer with SQLAlchemy models and proper connection management.
"""

import os
import logging
from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from contextlib import contextmanager
import uuid

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    google_id = Column(String, unique=True)
    wallet_address = Column(String, unique=True)
    display_name = Column(String)
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    projects = relationship("Project", back_populates="user")

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    project_type = Column(String, default='Article académique')
    style = Column(String, default='Académique')
    discipline = Column(String)
    status = Column(String, default='created')
    preferences = Column(JSON, default=dict)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="projects")
    sections = relationship("Section", back_populates="project", cascade="all, delete-orphan")
    versions = relationship("ProjectVersion", back_populates="project", cascade="all, delete-orphan")

class Section(Base):
    __tablename__ = 'sections'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey('projects.id'), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, default='')
    description = Column(Text)
    order_index = Column(Integer, default=0)
    fileverse_pad_id = Column(String)
    status = Column(String, default='draft')
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="sections")

class ProjectVersion(Base):
    __tablename__ = 'project_versions'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey('projects.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    description = Column(Text)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="versions")

class AIUsage(Base):
    __tablename__ = 'ai_usage'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    project_id = Column(String, ForeignKey('projects.id'))
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    cost_estimate = Column(String)
    model_used = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    """Professional database manager with connection pooling and error handling."""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection and create tables."""
        try:
            # Use SQLite for development, PostgreSQL for production
            db_url = os.getenv('DATABASE_URL', 'sqlite:///data/academic_writing.db')
            
            # Ensure data directory exists
            os.makedirs('data', exist_ok=True)
            
            self.engine = create_engine(
                db_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Session:
        """Get database session with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        with self.get_session() as session:
            return session.query(User).filter_by(email=email).first()
    
    def create_user(self, email: str, google_id: str = None, 
                   wallet_address: str = None, display_name: str = None) -> User:
        """Create a new user."""
        with self.get_session() as session:
            user = User(
                email=email,
                google_id=google_id,
                wallet_address=wallet_address,
                display_name=display_name or email.split('@')[0]
            )
            session.add(user)
            session.flush()
            return user
    
    def get_user_projects(self, user_id: str) -> List[Project]:
        """Get all projects for a user."""
        with self.get_session() as session:
            return session.query(Project).filter_by(user_id=user_id).order_by(Project.updated_at.desc()).all()
    
    def create_project(self, user_id: str, title: str, description: str = "", 
                      project_type: str = "Article académique", style: str = "Académique") -> Project:
        """Create a new project."""
        with self.get_session() as session:
            project = Project(
                user_id=user_id,
                title=title,
                description=description,
                project_type=project_type,
                style=style
            )
            session.add(project)
            session.flush()
            return project
    
    def track_ai_usage(self, user_id: str, project_id: str, prompt_tokens: int, 
                      completion_tokens: int, cost_estimate: str, model_used: str):
        """Track AI API usage for billing and monitoring."""
        with self.get_session() as session:
            usage = AIUsage(
                user_id=user_id,
                project_id=project_id,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost_estimate=cost_estimate,
                model_used=model_used
            )
            session.add(usage)

# Global database manager instance
db_manager = DatabaseManager()
