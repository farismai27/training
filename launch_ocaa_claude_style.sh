#!/bin/bash
# OCAA Web UI - Claude Style
# Matches claude.ai UI design

echo ""
echo "======================================================================"
echo " OCAA - Claude Style UI"
echo "======================================================================"
echo ""
echo " Matching claude.ai design:"
echo "   * Clean, minimalist interface"
echo "   * User messages on the right (dark bubbles)"
echo "   * Assistant messages on the left with avatar"
echo "   * Proper code highlighting"
echo "   * Smooth animations"
echo ""

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY not set"
    echo "   You'll need to enter it in the sidebar"
    echo ""
    read -p "Press Enter to continue..."
fi

# Launch the UI
echo "🚀 Starting OCAA Claude Style UI..."
echo ""
echo "Open your browser to: http://localhost:8501"
echo ""

streamlit run ocaa_web_ui_claude_style.py
