#!/bin/bash

# Academic Writing System Startup Script
echo "🚀 Starting Academic Writing System..."

# Check Python version
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1-2)
IFS='.' read -r python_major python_minor <<< "$python_version"
if (( python_major < 3 || ( python_major == 3 && python_minor < 8 ) )); then
    echo "❌ Python 3.8+ required. Current version: $python_version"
    exit 1
fi
echo "✅ Python version: $python_version"

# Check if required packages are installed
echo "🔍 Checking dependencies..."
missing_packages=()

packages=("streamlit" "sqlalchemy" "openai" "jwt" "google.auth" "pandas" "matplotlib" "plotly")
for package in "${packages[@]}"; do
    if ! python3 -c "import $package" 2>/dev/null; then
        if [[ "$package" == "jwt" ]]; then
            if ! python3 -c "import jwt" 2>/dev/null; then
                missing_packages+=("PyJWT")
            fi
        elif [[ "$package" == "google.auth" ]]; then
            if ! python3 -c "import google.auth" 2>/dev/null; then
                missing_packages+=("google-auth google-auth-oauthlib")
            fi
        else
            missing_packages+=("$package")
        fi
    fi
done

if [ ${#missing_packages[@]} -ne 0 ]; then
    echo "❌ Missing packages: ${missing_packages[*]}"
    echo "Installing missing packages..."
    pip3 install "${missing_packages[@]}"
fi

# Check if all core modules can import
echo "🔧 Checking core modules..."
python3 -c "
 import sys
 sys.path.append('.')

 modules_to_test = [
     'core.auth_system',
     'core.database_layer', 
     'core.config_manager',
     'modules.storyboard',
     'services.ai_service'
 ]

 failed_modules = []
 for module in modules_to_test:
     try:
         __import__(module)
     except Exception as e:
         failed_modules.append(f'{module}: {e}')

 if failed_modules:
     print('❌ Failed to import:')
     for failure in failed_modules:
         print(f'  - {failure}')
     exit(1)
 else:
     print('✅ All core modules imported successfully')
"

if [ $? -ne 0 ]; then
    echo "❌ Core module import failed. Please check dependencies."
    exit 1
fi

# Check if secrets are configured in Streamlit
echo "🔐 Checking Streamlit secrets configuration..."
python3 -c "
 import streamlit as st
 try:
     # Test if secrets are accessible
     secrets = st.secrets
     
     # Check for required secrets
     required_sections = ['google_oauth', 'openai']
     missing_secrets = []
     
     for section in required_sections:
         if section not in secrets:
             missing_secrets.append(section)
     
     if missing_secrets:
         print(f'❌ Missing secret sections: {missing_secrets}')
         print('Please configure secrets in Streamlit Cloud or add .streamlit/secrets.toml')
         exit(1)
     else:
         print('✅ Streamlit secrets configured')
         
 except Exception as e:
     print(f'⚠️  Secrets check failed: {e}')
     print('This is normal if running locally without secrets.toml')
"

# Initialize database if needed
echo "🗄️  Initializing database..."
python3 -c "
 from core.database_layer import db_manager
 try:
     db_manager.init_db()
     print('✅ Database initialized successfully')
 except Exception as e:
     print(f'❌ Database initialization failed: {e}')
     exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database initialization failed"
    exit 1
fi

# Start the application
echo "🌟 Starting Streamlit application..."
echo "📱 The app will be available at: http://localhost:8501"
echo ""

# Check if streamlit is in PATH, if not use direct path
if command -v streamlit &> /dev/null; then
    streamlit run app.py --server.port 8501
elif [ -f "$HOME/.local/bin/streamlit" ]; then
    "$HOME/.local/bin/streamlit" run app.py --server.port 8501
else
    echo "❌ Streamlit not found. Please ensure it's installed correctly."
    exit 1
fi