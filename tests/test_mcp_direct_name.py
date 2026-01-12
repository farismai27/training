#!/usr/bin/env python3
"""
Direct test of MCP server using 'name' argument schema.
"""
import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
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

    tools = await session.list_tools()
    print("Tools:", [t.name for t in tools.tools])

    res = await session.call_tool("list_documents", {})
    for c in getattr(res, 'content', []):
        print("list_documents:", getattr(c, 'text', ''))

    res = await session.call_tool("read_document", {"name": "kb-guide"})
    for c in getattr(res, 'content', []):
        print("read_document kb-guide:", getattr(c, 'text', '')[:200])

    await session.__aexit__(None, None, None)
    await stdio_transport.__aexit__(None, None, None)

if __name__ == "__main__":
    asyncio.run(main())
