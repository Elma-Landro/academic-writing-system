#!/bin/bash

echo "🚀 Academic Writing System - Quick Setup"
echo "========================================"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Run health check
echo "🏥 Running health check..."
python3 health_check.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup complete! Your Academic Writing System is ready."
    echo ""
    echo "Next steps:"
    echo "1. Configure your API keys in Streamlit Cloud secrets or .streamlit/secrets.toml"
    echo "2. Start the app with: ./start_app.sh"
    echo ""
    echo "Need help? Check SETUP_GUIDE.md for detailed instructions."
else
    echo ""
    echo "❌ Setup encountered issues. Please check the output above."
    echo "See SETUP_GUIDE.md for troubleshooting tips."
fi