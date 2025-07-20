#!/usr/bin/env python3

"""
Enhanced App Launcher for Academic Writing System
Handles Streamlit secrets configuration properly
"""

import os
import sys
import subprocess
import shutil
import importlib.util

def check_streamlit_installation():
    """Check if Streamlit is properly installed"""
    return importlib.util.find_spec("streamlit") is not None

def find_streamlit_command():
    """Find the streamlit command in various locations"""
    # Check if streamlit is in PATH
    if shutil.which('streamlit'):
        return 'streamlit'
    
    # Check common installation paths
    possible_paths = [
        os.path.expanduser('~/.local/bin/streamlit'),
        '/usr/local/bin/streamlit',
        sys.executable.replace('python', 'streamlit'),
    ]
    
    for path in possible_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    
    return None

def setup_streamlit_config():
    """Ensure .streamlit directory and config exist"""
    streamlit_dir = '.streamlit'
    
    if not os.path.exists(streamlit_dir):
        os.makedirs(streamlit_dir)
        print(f"✅ Created {streamlit_dir} directory")
    
    config_file = os.path.join(streamlit_dir, 'config.toml')
    if not os.path.exists(config_file):
        config_content = '''[server]
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
'''
        with open(config_file, 'w') as f:
            f.write(config_content)
        print(f"✅ Created {config_file}")

def check_secrets_info():
    """Check and provide info about secrets configuration"""
    secrets_file = '.streamlit/secrets.toml'
    
    if os.path.exists(secrets_file):
        print("✅ Local secrets file found")
        return True
    else:
        print("ℹ️  No local secrets file found")
        print("   If deploying to Streamlit Cloud, configure secrets in the dashboard")
        print("   For local development, create .streamlit/secrets.toml with your API keys")
        return False

def main():
    """Main launcher function"""
    print("🚀 Academic Writing System Launcher")
    print("=" * 40)
    
    # Check Streamlit installation
    if not check_streamlit_installation():
        print("❌ Streamlit not installed. Run: pip install streamlit")
        return 1
    
    # Find streamlit command
    streamlit_cmd = find_streamlit_command()
    if not streamlit_cmd:
        print("❌ Streamlit command not found")
        return 1
    
    print(f"✅ Found Streamlit: {streamlit_cmd}")
    
    # Setup configuration
    setup_streamlit_config()
    
    # Check secrets
    check_secrets_info()
    
    # Launch app
    print("\n🌟 Starting Academic Writing System...")
    print("📱 App will be available at: http://localhost:8501")
    print("Press Ctrl+C to stop\n")
    
    try:
        # Launch Streamlit
        cmd = [streamlit_cmd, 'run', 'app.py', '--server.port', '8501']
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())