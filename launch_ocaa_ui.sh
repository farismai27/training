#!/bin/bash
# OCAA Web UI Launcher for Linux/Mac
# Starts the custom OCAA Streamlit interface

echo ""
echo "======================================================================"
echo " Starting OCAA Web UI - OneSuite Core Architect Agent"
echo "======================================================================"
echo ""

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY not set in environment"
    echo "   You'll need to enter it in the web UI"
    echo ""
    echo "   To set it:"
    echo "   export ANTHROPIC_API_KEY='your-api-key-here'"
    echo ""
    read -p "Press Enter to continue..."
fi

# Check if streamlit is installed
python3 -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing Streamlit..."
    pip install streamlit
fi

# Launch the UI
echo "🚀 Starting OCAA Web UI..."
echo ""
echo "Once started, open your browser to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run ocaa_web_ui.py
