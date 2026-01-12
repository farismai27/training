#!/bin/bash
# Quick Start Script for Claude Computer Use

echo "=========================================="
echo "🤖 Claude Computer Use - Quick Start"
echo "=========================================="
echo ""

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY not set"
    echo ""
    echo "Please set your API key:"
    echo "  export ANTHROPIC_API_KEY='your-api-key-here'"
    echo ""
    exit 1
fi

echo "✅ API key found"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 not found"
    exit 1
fi

echo "✅ Python 3 found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q anthropic pillow pyautogui selenium playwright 2>&1 | grep -v "already satisfied" || true
echo "✅ Dependencies installed"
echo ""

# Start test server in background
echo "🚀 Starting test server..."
cd test-app
python3 server.py &
SERVER_PID=$!
cd ..

# Wait for server to start
sleep 2
echo "✅ Test server running at http://localhost:8000"
echo ""

# Open browser to test app
echo "🌐 Opening test app in browser..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8000 &> /dev/null
elif command -v open &> /dev/null; then
    open http://localhost:8000 &> /dev/null
else
    echo "   Please open http://localhost:8000 in your browser"
fi

echo ""
echo "=========================================="
echo "Ready to run Computer Use tests!"
echo "=========================================="
echo ""
echo "Options:"
echo ""
echo "1. Run automated QA tests:"
echo "   cd scripts"
echo "   python3 qa_test_mention_component.py"
echo ""
echo "2. Run custom task:"
echo "   cd scripts"
echo "   python3 computer_use_client.py 'your task here'"
echo ""
echo "3. Manual testing:"
echo "   Open http://localhost:8000 and test manually"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Wait for user interrupt
trap "kill $SERVER_PID 2>/dev/null; echo ''; echo '✋ Server stopped'; exit 0" INT
wait
