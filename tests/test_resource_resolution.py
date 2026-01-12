#!/usr/bin/env python3
"""
Direct test of resource resolution without interactive demo.
"""
import asyncio
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import re

async def test_resource_resolution():
    """Test fetching documents via MCP resources."""
    print("[TEST] Direct resource resolution test\n")
    
    # Connect to document server
    print("[1] Connecting to document server...")
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[os.path.join(os.path.dirname(__file__), "document_server.py")],
        env={}
    )
    
    transport = stdio_client(server_params)
    stdio, write = await transport.__aenter__()
    session = ClientSession(stdio, write)
    await session.__aenter__()
    await session.initialize()
    print("   [OK] Connected\n")
    
    # Test @ mention resolution
    test_text = "What's in @kb-guide and @document1? Tell me about both."
    print(f"[2] Input text: {test_text}\n")
    
    # Find mentions
    mention_pattern = r'@([a-zA-Z0-9\-_]+)'
    mentions = re.findall(mention_pattern, test_text)
    print(f"[3] Found mentions: {mentions}\n")
    
    # Fetch each mentioned document
    augmented_text = test_text
    for doc_name in set(mentions):
        try:
            resource_uri = f"docs://documents/{doc_name}"
            print(f"[4] Reading resource: {resource_uri}")
            result = await session.read_resource(resource_uri)
            
            # Extract content
            if hasattr(result, 'contents') and result.contents:
                for block in result.contents:
                    if hasattr(block, 'text'):
                        content = block.text
                        print(f"   [OK] Fetched {len(content)} bytes")
                        
                        # Replace mention with context
                        augmented_text = augmented_text.replace(
                            f"@{doc_name}",
                            f"[Document: {doc_name}]"
                        )
                        # Append document
                        augmented_text += f"\n\n---DOCUMENT: {doc_name}---\n{content}\n---"
        except Exception as e:
            print(f"   [ERROR] {str(e)}")
    
    print(f"\n[5] Augmented text (first 500 chars):\n")
    print(augmented_text[:500])
    print(f"\n... ({len(augmented_text)} total chars)")
    
    # Cleanup
    await session.__aexit__(None, None, None)
    await transport.__aexit__(None, None, None)
    print("\n[DONE] Resource resolution test complete!")

if __name__ == "__main__":
    asyncio.run(test_resource_resolution())
