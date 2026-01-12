#!/usr/bin/env python3
"""Test reading a document via MCP"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_read_document():
    """Test reading a document from MCP server"""
    # Connect to document server
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[os.path.join(os.path.dirname(__file__), "document_server.py")],
        env={}
    )
    
    print("[TEST] Connecting to document server...")
    stdio_transport = stdio_client(server_params)
    stdio, write = await stdio_transport.__aenter__()
    
    session = ClientSession(stdio, write)
    await session.__aenter__()
    await session.initialize()
    
    print("[OK] Connected!")
    
    # List documents
    print("\n[TEST] Listing documents...")
    list_result = await session.call_tool("list_documents", {})
    for content in list_result.content:
        print(f"  {content.text}")
    
    # Read the KB guide
    print("\n[TEST] Reading kb-guide document...")
    result = await session.call_tool("read_document", {"document_id": "kb-guide"})
    for content in result.content:
        print(f"{content.text}")
    
    # Clean up
    await session.__aexit__(None, None, None)
    await stdio_transport.__aexit__(None, None, None)

if __name__ == "__main__":
    asyncio.run(test_read_document())
