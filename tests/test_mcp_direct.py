#!/usr/bin/env python3
"""
Direct test of MCP tool execution via execute_tool function.
"""
import sys
import os

# Add workspace to path
sys.path.insert(0, '/c/Users/farismai2/coding/training')

# Configure to avoid the interactive prompts
os.environ['PYTHONUNBUFFERED'] = '1'

import asyncio
from concurrent.futures import ThreadPoolExecutor
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json

# Test directly
async def test_mcp():
    """Test MCP connection and tool execution."""
    print("[TEST] Starting MCP test...\n")
    
    # Initialize MCP server
    print("[1] Connecting to document server...")
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[os.path.join(os.path.dirname(__file__), "document_server.py")],
        env={}
    )
    
    stdio_transport = stdio_client(server_params)
    stdio, write = await stdio_transport.__aenter__()
    session = ClientSession(stdio, write)
    await session.__aenter__()
    await session.initialize()
    print("[1] Connected!\n")
    
    # List tools
    print("[2] Listing available tools...")
    tools_response = await session.list_tools()
    for tool in tools_response.tools:
        print(f"    - {tool.name}")
    print()
    
    # Call list_documents tool
    print("[3] Calling list_documents tool...")
    try:
        result = await session.call_tool("list_documents", {})
        print(f"    Success! Result type: {type(result)}")
        if hasattr(result, 'content'):
            for content_block in result.content:
                if hasattr(content_block, 'text'):
                    print(f"    Content: {content_block.text}")
    except Exception as e:
        print(f"    ERROR: {e}")
    print()
    
    # Call read_document tool
    print("[4] Calling read_document tool...")
    try:
        result = await session.call_tool("read_document", {"document_id": "kb-guide"})
        print(f"    Success! Result type: {type(result)}")
        if hasattr(result, 'content'):
            for content_block in result.content:
                if hasattr(content_block, 'text'):
                    content_text = content_block.text[:200] + "..." if len(content_block.text) > 200 else content_block.text
                    print(f"    Content: {content_text}")
    except Exception as e:
        print(f"    ERROR: {e}")
    print()
    
    # Cleanup
    print("[5] Closing connection...")
    await session.__aexit__(None, None, None)
    await stdio_transport.__aexit__(None, None, None)
    print("[5] Done!")

# Run the test
asyncio.run(test_mcp())
