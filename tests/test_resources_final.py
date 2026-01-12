#!/usr/bin/env python3
"""Test MCP Resources implementation."""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_resources():
    """Test reading resources from the document server."""
    
    # Configure server connection
    server_params = StdioServerParameters(
        command=".venv/Scripts/python",
        args=["document_server.py"]
    )
    
    # Create stdio client context
    stdio_transport = stdio_client(server_params)
    stdio, write = await stdio_transport.__aenter__()
    
    try:
        # Create session
        session = ClientSession(stdio, write)
        await session.__aenter__()
        
        # Initialize
        await session.initialize()
        
        print("=" * 60)
        print("Testing MCP Resources Implementation")
        print("=" * 60)
        
        # Test 1: Direct resource - list documents
        print("\n1. Testing Direct Resource: docs://documents")
        print("   (Returns list of all documents as JSON)")
        try:
            result = await session.read_resource("docs://documents")
            if result and hasattr(result, 'contents') and result.contents:
                content = result.contents[0]
                print(f"   MIME Type: {content.mimeType if hasattr(content, 'mimeType') else 'unknown'}")
                print(f"   Content: {content.text if hasattr(content, 'text') else str(content)}")
                docs = json.loads(content.text if hasattr(content, 'text') else str(content))
                print(f"   Parsed: {docs}")
                print("   Status: PASS")
        except Exception as e:
            print(f"   Error: {e}")
            print("   Status: FAIL")
        
        # Test 2: Templated resource - fetch specific document
        print("\n2. Testing Templated Resource: docs://documents/document1")
        print("   (Returns specific document content as text/plain)")
        try:
            result = await session.read_resource("docs://documents/document1")
            if result and hasattr(result, 'contents') and result.contents:
                content = result.contents[0]
                print(f"   MIME Type: {content.mimeType if hasattr(content, 'mimeType') else 'unknown'}")
                print(f"   Content: {content.text if hasattr(content, 'text') else str(content)}")
                print("   Status: PASS")
        except Exception as e:
            print(f"   Error: {e}")
            print("   Status: FAIL")
        
        # Test 3: Templated resource - fetch kb-guide
        print("\n3. Testing Templated Resource: docs://documents/kb-guide")
        try:
            result = await session.read_resource("docs://documents/kb-guide")
            if result and hasattr(result, 'contents') and result.contents:
                content = result.contents[0]
                print(f"   MIME Type: {content.mimeType if hasattr(content, 'mimeType') else 'unknown'}")
                print(f"   Content: {content.text if hasattr(content, 'text') else str(content)}")
                print("   Status: PASS")
        except Exception as e:
            print(f"   Error: {e}")
            print("   Status: FAIL")
        
        # Test 4: Invalid resource - should error gracefully
        print("\n4. Testing Invalid Resource: docs://documents/nonexistent")
        print("   (Should raise error)")
        try:
            result = await session.read_resource("docs://documents/nonexistent")
            print("   Status: FAIL (should have errored)")
        except Exception as e:
            print(f"   Error (expected): {e}")
            print("   Status: PASS")
        
        print("\n" + "=" * 60)
        print("Resource Testing Complete")
        print("=" * 60)
    finally:
        try:
            await session.__aexit__(None, None, None)
            await stdio_transport.__aexit__(None, None, None)
        except:
            pass


if __name__ == "__main__":
    asyncio.run(test_resources())
