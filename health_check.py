#!/usr/bin/env python3
"""Health check script for Academic Writing System"""

import sys
import os
import importlib.util
sys.path.append('.')

def check_dependencies():
    """Check if all required dependencies are installed"""
    required = ['streamlit', 'sqlalchemy', 'openai', 'google.auth']
    missing = []

    for package in required:
        try:
            if package == 'openai':
                spec = importlib.util.find_spec('openai')
                if spec is None:
                    raise ImportError
            elif package == 'google.auth':
                spec = importlib.util.find_spec('google.auth')
                if spec is None:
                    raise ImportError
            else:
                __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing.append(package)
            print(f"✗ {package}")

    return len(missing) == 0

def check_modules():
    """Check if core application modules can import"""
    modules = [
        'core.auth_system',
        'core.database_layer', 
        'core.config_manager',
        'modules.storyboard',
        'services.ai_service'
    ]

    success = 0
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
            success += 1
        except Exception as e:
            print(f"✗ {module}: {e}")

    return success == len(modules)

def check_config():
    """Check if configuration files exist"""
    config_files = ['.streamlit/secrets.toml', 'secrets.toml']
    found = False

    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✓ {config_file} exists")
            found = True
        else:
            print(f"⚠ {config_file} not found")

    return found

if __name__ == "__main__":
    print("=== Academic Writing System Health Check ===\n")

    print("1. Checking Dependencies:")
    deps_ok = check_dependencies()

    print("\n2. Checking Application Modules:")
    modules_ok = check_modules()

    print("\n3. Checking Configuration:")
    config_ok = check_config()

    print("\n=== Summary ===")
    print(f"Dependencies: {'✓' if deps_ok else '✗'}")
    print(f"Modules: {'✓' if modules_ok else '✗'}")
    print(f"Configuration: {'✓' if config_ok else '⚠'}")

    if deps_ok and modules_ok:
        print("\n🎉 System is ready to run!")
        print("Start with: streamlit run app.py")
    else:
        print("\n❌ System needs setup. See STARTUP_GUIDE.md")