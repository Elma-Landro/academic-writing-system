#!/usr/bin/env python3
"""
Health Check Script for Academic Writing System
Verifies all components are working correctly
"""

import sys
import importlib.util
sys.path.append('.')

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    modules = [
        ('streamlit', 'Streamlit web framework'),
        ('sqlalchemy', 'Database ORM'),
        ('openai', 'OpenAI API client'),
        ('jwt', 'JWT token handling'),
        ('google.auth', 'Google OAuth'),
        ('pandas', 'Data manipulation'),
        ('matplotlib', 'Plotting library'),
        ('plotly', 'Interactive plots')
    ]
    
    failed_imports = []
    
    for module_name, description in modules:
        try:
            if module_name in ('jwt', 'google.auth'):
                spec = importlib.util.find_spec(module_name)
                if spec is None:
                    raise ImportError(f"No module named {module_name}")
            else:
                __import__(module_name)
            print(f"✅ {module_name:15} - {description}")
        except ImportError as e:
            print(f"❌ {module_name:15} - {description} (Error: {e})")
            failed_imports.append(module_name)
    
    return failed_imports

def test_core_modules():
    """Test core application modules"""
    print("\n🔧 Testing core application modules...")
    
    core_modules = [
        'core.auth_system',
        'core.database_layer',
        'core.config_manager',
        'core.integration_layer',
        'modules.storyboard',
        'modules.redaction',
        'modules.revision',
        'modules.finalisation',
        'services.ai_service'
    ]
    
    failed_modules = []
    
    for module in core_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module} - Error: {e}")
            failed_modules.append(module)
    
    return failed_modules

def test_database():
    """Test database connectivity"""
    print("\n🗄️  Testing database...")
    
    try:
        from core.database_layer import db_manager
        db_manager.init_db()
        print("✅ Database initialization successful")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_secrets():
    """Test secrets configuration"""
    print("\n🔐 Testing secrets configuration...")
    
    try:
        import streamlit as st
        secrets = st.secrets
        
        required_sections = ['google_oauth', 'openai']
        missing_sections = []
        
        for section in required_sections:
            if section not in secrets:
                missing_sections.append(section)
                
        if missing_sections:
            print(f"⚠️  Missing secret sections: {missing_sections}")
            print("   Configure these in Streamlit Cloud secrets or .streamlit/secrets.toml")
            return False
        else:
            print("✅ All required secret sections found")
            return True
            
    except Exception as e:
        print(f"⚠️  Secrets check failed: {e}")
        print("   This is normal if running locally without proper secrets configuration")
        return False

def main():
    """Run all health checks"""
    print("🏥 Academic Writing System Health Check")
    print("=" * 50)
    
    # Test imports
    failed_imports = test_imports()
    
    # Test core modules
    failed_modules = test_core_modules()
    
    # Test database
    db_ok = test_database()
    
    # Test secrets
    secrets_ok = test_secrets()
    
    # Summary
    print("\n📋 Health Check Summary")
    print("=" * 30)
    
    if not failed_imports and not failed_modules and db_ok:
        print("✅ System Status: HEALTHY")
        print("🚀 Ready to start with: ./start_app.sh")
        return 0
    else:
        print("❌ System Status: ISSUES DETECTED")
        
        if failed_imports:
            print(f"   Missing packages: {', '.join(failed_imports)}")
            print("   Run: pip install -r requirements.txt")
            
        if failed_modules:
            print(f"   Failed modules: {', '.join(failed_modules)}")
            
        if not db_ok:
            print("   Database issues detected")
            
        if not secrets_ok:
            print("   Secrets configuration needed")
            
        return 1

if __name__ == "__main__":
    sys.exit(main())