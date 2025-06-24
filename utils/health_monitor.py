
"""
System health monitoring and diagnostics.
"""

import time
import psutil
import streamlit as st
from typing import Dict, Any
from datetime import datetime

class HealthMonitor:
    """Monitor system health and performance."""
    
    @staticmethod
    def get_system_health() -> Dict[str, Any]:
        """Get comprehensive system health status."""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "memory": {
                    "used_mb": psutil.virtual_memory().used / 1024 / 1024,
                    "available_mb": psutil.virtual_memory().available / 1024 / 1024,
                    "percent": psutil.virtual_memory().percent
                },
                "cpu_percent": psutil.cpu_percent(),
                "disk": {
                    "used_gb": psutil.disk_usage('/').used / 1024 / 1024 / 1024,
                    "free_gb": psutil.disk_usage('/').free / 1024 / 1024 / 1024
                },
                "session_state_size": len(str(st.session_state)),
                "status": "healthy"
            }
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }
    
    @staticmethod
    def check_dependencies() -> Dict[str, bool]:
        """Check if all dependencies are available."""
        checks = {}
        
        # Check OpenAI API
        try:
            import openai
            checks["openai"] = True
        except ImportError:
            checks["openai"] = False
        
        # Check Google APIs
        try:
            from googleapiclient.discovery import build
            checks["google_apis"] = True
        except ImportError:
            checks["google_apis"] = False
        
        # Check database
        try:
            import sqlite3
            checks["database"] = True
        except ImportError:
            checks["database"] = False
        
        return checks
