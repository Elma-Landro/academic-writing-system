
"""
Database layer using SQLite for reliable data persistence.
Replaces the broken JSON file system.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import threading

class DatabaseManager:
    """Thread-safe database manager for persistent storage."""
    
    def __init__(self, db_path: str = "data/academic_writing.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.local = threading.local()
        self._ensure_tables()
    
    def _get_connection(self):
        """Get thread-local database connection."""
        if not hasattr(self.local, 'connection'):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self.local.connection.row_factory = sqlite3.Row
        return self.local.connection
    
    def _ensure_tables(self):
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    project_type TEXT,
                    data JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS project_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    version_name TEXT NOT NULL,
                    data JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                );
                
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id TEXT PRIMARY KEY,
                    data JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_projects_updated 
                ON projects (updated_at DESC);
                
                CREATE INDEX IF NOT EXISTS idx_versions_project 
                ON project_versions (project_id, created_at DESC);
            """)
    
    def save_project(self, project_id: str, data: Dict[str, Any]) -> bool:
        """Save project data safely."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO projects 
                    (id, title, description, project_type, data, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    project_id,
                    data.get('title', ''),
                    data.get('description', ''),
                    data.get('project_type', ''),
                    json.dumps(data)
                ))
                return True
        except Exception as e:
            print(f"Database error saving project: {e}")
            return False
    
    def load_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load project data safely."""
        try:
            with self._get_connection() as conn:
                row = conn.execute(
                    "SELECT data FROM projects WHERE id = ?",
                    (project_id,)
                ).fetchone()
                
                if row:
                    return json.loads(row['data'])
                return None
        except Exception as e:
            print(f"Database error loading project: {e}")
            return None
