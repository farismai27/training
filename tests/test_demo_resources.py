#!/usr/bin/env python3
"""
Automated test of demo with @ mention resource resolution.
"""
import sys
import os
import json
import asyncio
from subprocess import Popen, PIPE

# Add workspace to path
sys.path.insert(0, 'c:\\Users\\farismai2\\coding\\training')

# Import directly to test
from demo import initialize_mcp_servers, call_ocaa_with_tools, mcp_sessions

async def test_resources():
    """Test @ mention resource resolution."""
    print("[TEST] Starting automated resource test...\n")
    
    # Initialize MCP servers
    print("[1] Initializing MCP servers...")
    await initialize_mcp_servers()
    print(f"   Discovered {len(mcp_sessions)} server(s)\n")
    
    # Test question with @ mention
    question = "What's in @kb-guide? Give me a summary."
    print(f"[2] Testing question: {question}\n")
    
    # Call with tools (this will resolve @ mention and get document content)
    print("[3] Calling OCAA with tools...\n")
    try:
        response = call_ocaa_with_tools(question, max_iterations=3)
        print(f"\n[RESPONSE]\n{response}")
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_resources())
