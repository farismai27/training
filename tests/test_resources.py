#!/usr/bin/env python3
"""Test MCP server resources."""
import asyncio
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    print("[TEST] Starting resource test...\n")
    
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
    print("[1] Connected to server\n")
    
    # List resources
    print("[2] Listing resources...")
    resources_resp = await session.list_resources()
    print(f"   Found {len(resources_resp.resources)} resources:")
    for res in resources_resp.resources:
        print(f"     - {res.uri}: {res.name}")
    print()
    
    # Read direct resource: docs://documents
    print("[3] Reading docs://documents (document list)...")
    result = await session.read_resource("docs://documents")
    print(f"   Content blocks: {len(result.contents)}")
    if result.contents and hasattr(result.contents[0], 'text'):
        print(f"   Data: {result.contents[0].text}")
    print()
    
    # Read templated resource: docs://documents/{name}
    print("[4] Reading docs://documents/kb-guide (document content)...")
    result = await session.read_resource("docs://documents/kb-guide")
    print(f"   Content blocks: {len(result.contents)}")
    if result.contents and hasattr(result.contents[0], 'text'):
        text = result.contents[0].text
        preview = text[:100] + "..." if len(text) > 100 else text
        print(f"   Data: {preview}")
    print()
    
    # Cleanup
    await session.__aexit__(None, None, None)
    await transport.__aexit__(None, None, None)
    print("[DONE] Resource test complete!")

if __name__ == "__main__":
    asyncio.run(main())
