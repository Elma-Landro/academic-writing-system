# 🚀 Quick Startup Guide - Academic Writing System

## Prerequisites Check
✅ Python 3.8+ installed
✅ All dependencies installed from requirements.txt
✅ API keys configured in secrets.toml

## Installation Steps

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Configure API Keys
Edit `.streamlit/secrets.toml` with your real API keys:

```toml
[google_oauth]
client_id = "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"

[openai]
api_key = "sk-proj-YOUR_OPENAI_API_KEY_HERE"
```

**Required API Keys:**
- **Google OAuth**: Get from [Google Cloud Console](https://console.cloud.google.com/)
- **OpenAI API**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Optional**: Venice AI, Fileverse for additional features

### 3. Start Application
```bash
# Method 1: If streamlit is in PATH
streamlit run app.py

# Method 2: Direct path (if needed)
$HOME/.local/bin/streamlit run app.py

# Method 3: Custom port
streamlit run app.py --server.port 8501
```

### 4. Access Application
- Open browser to: `http://localhost:8501`
- Complete Google OAuth setup when prompted
- Start using the academic writing system!

## Troubleshooting

### Common Issues
1. **Import errors**: Run `pip3 install -r requirements.txt`
2. **Config errors**: Ensure `.streamlit/secrets.toml` exists with valid API keys
3. **Port conflicts**: Use `--server.port XXXX` to change port
4. **OAuth issues**: Verify Google Cloud Console setup

### Health Check
```bash
# Test all modules import correctly
python3 -c "
import sys
sys.path.append('.')
modules = ['core.auth_system', 'core.database_layer', 'modules.storyboard']
for module in modules:
    try:
        __import__(module)
        print(f'✓ {module}')
    except Exception as e:
        print(f'✗ {module}: {e}')
"
```

## Features Available After Setup

### 🎨 Core Modules
- **Storyboard Engine**: AI-powered academic structure generation
- **Writing Assistant**: Contextual writing help with AI
- **Revision Tools**: Quality analysis and improvement suggestions  
- **Export Features**: Multiple format exports (Markdown, HTML, LaTeX, PDF)

### 👤 User Features
- **OAuth Authentication**: Secure Google login
- **Project Management**: Persistent project contexts
- **Adaptive Learning**: System learns your writing preferences
- **Analytics Dashboard**: Writing metrics and progress tracking

### 🔧 Technical Features
- **SQLite Database**: All user data and projects stored locally
- **Intelligent Caching**: Optimized API usage and performance
- **Modular Architecture**: Easy to extend and customize
- **Multi-format Export**: Professional document output

## Next Steps After Setup
1. **Configure API Keys**: Add your real OpenAI and Google OAuth credentials
2. **Create First Project**: Test the storyboard generation
3. **Explore Features**: Try each of the 4 workflow phases
4. **Customize Settings**: Adapt the system to your writing style

🎯 **Your academic writing system is now ready to revolutionize your workflow!**