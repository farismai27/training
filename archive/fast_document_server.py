#!/usr/bin/env python3
"""
FastMCP Document Server (Inspector-friendly)
Provides in-memory document storage via MCP protocol with FastMCP.
Use with `mcp dev fast_document_server.py` for the MCP Inspector.
"""

import asyncio
import json
from mcp.server.fastmcp.server import FastMCP

DOCUMENTS: dict[str, str] = {
    "document1": "OneSuite Core architecture overview and design principles.",
    "document2": "Q1-Q2 2026 product roadmap with milestones and deliverables.",
    "document3": "User story templates and acceptance criteria guidelines.",
    "kb-guide": "Knowledge base navigation for Search, Social, Programmatic, Commerce channels.",
}

server = FastMCP("document-server")

@server.tool(name="list_documents", description="List all available document names.")
def list_documents() -> str:
    return json.dumps({
        "documents": list(DOCUMENTS.keys()),
        "count": len(DOCUMENTS),
    })

@server.tool(name="read_document", description="Read a document by ID or name.")
def read_document(name: str | None = None, document_id: str | None = None) -> str:
    key = document_id or name or ""
    if key not in DOCUMENTS:
        return f"Error: Document '{key}' not found. Available documents: {', '.join(DOCUMENTS.keys())}"
    return DOCUMENTS[key]

@server.tool(name="update_document", description="Update or create a document.")
def update_document(content: str, name: str | None = None, document_id: str | None = None) -> str:
    key = document_id or name or ""
    is_new = key not in DOCUMENTS
    DOCUMENTS[key] = content
    return json.dumps({
        "success": True,
        "action": "created" if is_new else "updated",
        "document_id": key,
        "length": len(content),
    })

if __name__ == "__main__":
    asyncio.run(server.run_stdio_async())
