#!/usr/bin/env python3
"""
Simple test of @ mention resolution using tools.
"""
import sys
sys.path.insert(0, 'c:\\Users\\farismai2\\coding\\training')

import asyncio
from demo import initialize_mcp_servers, resolve_mentions_in_text

async def test():
    print("[TEST] @ Mention resolution test\n")
    
    # Initialize MCP
    print("[1] Initializing MCP servers...")
    await initialize_mcp_servers()
    print("   [OK]\n")
    
    # Test @ mention
    test_input = "What's in @kb-guide and @document1?"
    print(f"[2] Input: {test_input}\n")
    
    # Resolve mentions
    print("[3] Resolving @mentions using read_document tool...")
    result = resolve_mentions_in_text(test_input)
    
    print(f"\n[OUTPUT] (first 800 chars):\n")
    print(result[:800])
    print(f"\n... ({len(result)} total chars)")

if __name__ == "__main__":
    asyncio.run(test())
