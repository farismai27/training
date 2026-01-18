#!/bin/bash
# Launch Anthropic's Computer Use Reference Implementation
# This provides the EXACT web UI from the lesson!

echo "=========================================="
echo "🖥️  Anthropic Computer Use Reference"
echo "   Official Implementation with Web UI"
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

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker not found"
    echo ""
    echo "Please install Docker:"
    echo "  Windows: https://docs.docker.com/desktop/install/windows-install/"
    echo "  Mac: https://docs.docker.com/desktop/install/mac-install/"
    echo "  Linux: https://docs.docker.com/engine/install/"
    echo ""
    exit 1
fi

echo "✅ Docker found"
echo ""

# Pull the latest image
echo "📦 Pulling latest Computer Use image..."
docker pull ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest

echo ""
echo "=========================================="
echo "🚀 Starting Computer Use Demo"
echo "=========================================="
echo ""

# Run the container
docker run \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5900:5900 \
    -p 8501:8501 \
    -p 6080:6080 \
    -p 8080:8080 \
    -it \
    --name computer-use-demo \
    ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest

# Note: The container will start and show instructions
# User can access the UI at http://localhost:8080
