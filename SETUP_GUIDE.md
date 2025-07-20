# 🚀 Academic Writing System - Complete Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Streamlit Secrets

#### Option A: Streamlit Cloud (Recommended)
1. Deploy to Streamlit Cloud
2. Go to your app settings → Secrets
3. Add the following secrets:

```toml
[google_oauth]
client_id = "your-google-client-id.googleusercontent.com"
client_secret = "your-google-client-secret"

[openai]
api_key = "sk-proj-your-openai-api-key"
```

#### Option B: Local Development
Create `.streamlit/secrets.toml`:

```toml
[google_oauth]
client_id = "your-google-client-id.googleusercontent.com"
client_secret = "your-google-client-secret"

[openai]
api_key = "sk-proj-your-openai-api-key"
```

### 3. Run Health Check
```bash
python3 health_check.py
```

### 4. Start Application
```bash
./start_app.sh
```

Or manually:
```bash
streamlit run app.py --server.port 8501
```

## Getting API Keys

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add your domain to authorized origins
6. Add redirect URI: `https://your-app-url/auth/callback`

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-proj-` or `sk-`)

## Troubleshooting

### Common Issues

#### "Module not found" errors
```bash
pip install -r requirements.txt
```

#### "Secrets not configured"
- Check Streamlit Cloud secrets configuration
- For local development, ensure `.streamlit/secrets.toml` exists

#### Database errors
```bash
python3 -c "from core.database_layer import db_manager; db_manager.init_db()"
```

#### Permission errors on scripts
```bash
chmod +x start_app.sh health_check.py
```

### Debug Mode
Set environment variable for detailed logging:
```bash
export ACADEMIC_WRITING_DEBUG=true
export ACADEMIC_WRITING_LOG_LEVEL=DEBUG
```

## System Requirements

- Python 3.8+
- 2GB RAM minimum
- Internet connection for AI services
- Modern web browser

## Security Notes

- Never commit actual API keys to version control
- Use Streamlit Cloud secrets for production
- Regularly rotate API keys
- Monitor API usage and costs

---

✅ **Ready to revolutionize your academic writing with AI assistance!**