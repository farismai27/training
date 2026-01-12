#!/usr/bin/env python3
"""Test @mention resolution using MCP Resources."""

import asyncio
import json
import re
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from concurrent.futures import ThreadPoolExecutor

mcp_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="mcp-")
mcp_sessions = {}


async def read_resource_async(session, resource_uri: str) -> str:
    """Read a resource via MCP Resource API."""
    try:
        result = await session.read_resource(resource_uri)
        
        if result and hasattr(result, 'contents') and result.contents:
            content_block = result.contents[0]
            if hasattr(content_block, 'text'):
                return content_block.text
            else:
                return str(content_block)
        
        return ""
    except Exception as e:
        print(f"[ERROR] read_resource_async error: {str(e)}")
        raise


async def resolve_mentions_in_text_async(text: str, session) -> str:
    """Resolve @document mentions using MCP Resources (async version)."""
    mention_pattern = r'@([a-zA-Z0-9\-_]+)'
    mentions = re.findall(mention_pattern, text)
    
    if not mentions:
        return text
    
    augmented_text = text
    for doc_name in set(mentions):
        try:
            resource_uri = f"docs://documents/{doc_name}"
            content = await read_resource_async(session, resource_uri)
            
            if content:
                print(f"[SUCCESS] Fetched resource {resource_uri}: {len(content)} chars")
                augmented_text = augmented_text.replace(
                    f"@{doc_name}",
                    f"[Document: {doc_name}]"
                )
                augmented_text += f"\n\n---\n[Referenced Document: {doc_name}]\n{content}\n---"
            else:
                print(f"[WARNING] No content for @{doc_name}")
        except Exception as e:
            print(f"[ERROR] Failed to fetch @{doc_name}: {str(e)}")
    
    return augmented_text


async def initialize_mcp_server():
    """Connect to document server."""
    global mcp_sessions
    
    print("Initializing MCP document server...")
    
    server_params = StdioServerParameters(
        command=".venv/Scripts/python",
        args=["document_server.py"]
    )
    
    stdio_transport = stdio_client(server_params)
    stdio, write = await stdio_transport.__aenter__()
    
    session = ClientSession(stdio, write)
    await session.__aenter__()
    await session.initialize()
    
    mcp_sessions["documents"] = session
    print("Document server connected.\n")


async def test_mentions():
    """Test @ mention resolution."""
    try:
        await initialize_mcp_server()
        
        session = mcp_sessions["documents"]
        test_text = "Please show me @kb-guide and also @document1"
        print("=" * 60)
        print("Testing @mention Resolution")
        print("=" * 60)
        print(f"\nOriginal text: {test_text}")
        print("\nResolving mentions...")
        
        result = await resolve_mentions_in_text_async(test_text, session)
        
        print("\n" + "=" * 60)
        print("Result:")
        print("=" * 60)
        print(result)
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mentions())
