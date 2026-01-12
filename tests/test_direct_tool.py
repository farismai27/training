#!/usr/bin/env python3
"""Test @ mention resolution in isolation."""
import sys
sys.path.insert(0, 'c:\\Users\\farismai2\\coding\\training')

from demo import mcp_sessions, mcp_tools, is_mcp_tool, execute_tool, MCP_SERVERS_CONFIG
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json

async def init_and_test():
    print("[INIT] Setting up MCP...\n")
    
    # Manually initialize one server
    config = MCP_SERVERS_CONFIG["documents"]
    server_params = StdioServerParameters(
        command=config["command"],
        args=config.get("args", []),
        env=config.get("env", {})
    )
    
    stdio_transport = stdio_client(server_params)
    stdio, write = await stdio_transport.__aenter__()
    session = ClientSession(stdio, write)
    await session.__aenter__()
    await session.initialize()
    
    print("[OK] Connected to server\n")
    
    # Test tool call
    print("[TEST] Calling read_document(@kb-guide)...")
    result = await session.call_tool("read_document", {"name": "kb-guide"})
    print(f"Result type: {type(result)}")
    print(f"Result content blocks: {len(result.content) if hasattr(result, 'content') else 'N/A'}")
    
    if hasattr(result, 'content'):
        for i, block in enumerate(result.content):
            text = block.text if hasattr(block, 'text') else str(block)
            print(f"  Block {i}: {text[:100]}...\n")
    
    # Cleanup
    await session.__aexit__(None, None, None)
    await stdio_transport.__aexit__(None, None, None)
    print("[DONE]")

asyncio.run(init_and_test())
