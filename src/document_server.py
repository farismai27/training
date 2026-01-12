#!/usr/bin/env python3
"""
Document Management MCP Server
Provides in-memory document storage via MCP protocol with Resources.
"""

import asyncio
import json
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, ListResourcesResult, TextContent, Tool, GetPromptResult, PromptMessage
from document_utils import document_path_to_markdown

# Load OneSuite User Stories from file
def load_user_stories():
    """Load user stories markdown file if it exists."""
    user_stories_path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "onesuite_user_stories.md")
    if os.path.exists(user_stories_path):
        try:
            with open(user_stories_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error loading user stories: {str(e)}"
    return None

# In-memory document storage
DOCUMENTS = {
    "document1": "OneSuite Core architecture overview and design principles.",
    "document2": "Q1-Q2 2026 product roadmap with milestones and deliverables.",
    "document3": "User story templates and acceptance criteria guidelines.",
    "kb-guide": "Knowledge base navigation for Search, Social, Programmatic, Commerce channels.",
}

# Add OneSuite Platform User Stories if available
user_stories_content = load_user_stories()
if user_stories_content:
    DOCUMENTS["onesuite-user-stories"] = user_stories_content

# Create MCP server
server = Server("document-server")

# ============================================================================
# MCP TOOLS - For tool discovery
# ============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools (for backward compatibility)."""
    return [
        Tool(
            name="read_document",
            description="Read a document by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Document name"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="update_document",
            description="Update or create a document with new content",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Document name"},
                    "content": {"type": "string", "description": "New document content"}
                },
                "required": ["name", "content"]
            }
        ),
        Tool(
            name="document_path_to_markdown",
            description="Read a PDF or Word document from file system and convert to Markdown",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the PDF (.pdf) or Word (.docx) document"}
                },
                "required": ["file_path"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute tool calls (for backward compatibility)."""
    if name == "read_document":
        doc_name = arguments.get("name", "")
        if doc_name not in DOCUMENTS:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Document '{doc_name}' not found"})
            )]
        return [TextContent(
            type="text",
            text=json.dumps({"name": doc_name, "content": DOCUMENTS[doc_name]})
        )]
    
    elif name == "update_document":
        doc_name = arguments.get("name", "")
        content = arguments.get("content", "")

        if not doc_name or not content:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "Both 'name' and 'content' required"})
            )]

        is_new = doc_name not in DOCUMENTS
        DOCUMENTS[doc_name] = content

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "action": "created" if is_new else "updated",
                "name": doc_name
            })
        )]

    elif name == "document_path_to_markdown":
        file_path = arguments.get("file_path", "")

        if not file_path:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "'file_path' is required"})
            )]

        try:
            markdown_content = document_path_to_markdown(file_path)
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "file_path": file_path,
                    "markdown": markdown_content
                })
            )]
        except FileNotFoundError as e:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"File not found: {str(e)}"})
            )]
        except ValueError as e:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unsupported file type: {str(e)}"})
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Conversion failed: {str(e)}"})
            )]

    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

# ============================================================================
# MCP RESOURCES - Lesson Implementation (using SDK patterns)
# ============================================================================

@server.list_resources()
async def list_resources() -> ListResourcesResult:
    """List available resources (both direct and templated)."""
    return ListResourcesResult(
        resources=[
            Resource(
                uri="docs://documents",
                name="Document List",
                description="List of all available document names (JSON)",
                mimeType="application/json"
            ),
            Resource(
                uri="docs://documents/{name}",
                name="Document Content",
                description="Contents of a specific document by name (text/plain)",
                mimeType="text/plain"
            )
        ]
    )


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource by URI.
    
    Implements two resource types:
    1. Direct resource: docs://documents → returns JSON list of doc names
    2. Templated resource: docs://documents/{doc_id} → returns document content as text
    """
    # Convert URI to string (it may come as AnyUrl object)
    uri_str = str(uri)
    
    if uri_str == "docs://documents":
        # Direct resource: return list of document names as JSON
        return json.dumps(list(DOCUMENTS.keys()))
    
    elif uri_str.startswith("docs://documents/"):
        # Templated resource: fetch document content by name
        doc_name = uri_str.replace("docs://documents/", "")
        if doc_name not in DOCUMENTS:
            raise ValueError(f"Doc with id {doc_name} not found")
        return DOCUMENTS[doc_name]
    
    else:
        raise ValueError(f"Unknown resource URI: {uri_str}")

# ============================================================================
# MCP PROMPTS - Pre-defined, well-tested prompts
# ============================================================================

@server.list_prompts()
async def list_prompts() -> list[dict]:
    """List available prompts."""
    return [
        {
            "name": "format",
            "description": "Rewrites the contents of a document in Markdown format",
            "arguments": [
                {
                    "name": "doc_id",
                    "description": "ID of the document to format",
                    "required": True
                }
            ]
        }
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    """Get a specific prompt by name with arguments."""
    
    if name == "format":
        doc_id = arguments.get("doc_id", "")
        
        # Well-tested, well-evaled prompt for document formatting
        prompt_text = f"""Please help me reformat a document into proper Markdown syntax.

Document ID: {doc_id}

Instructions:
1. First, use the read_document tool to fetch the content of the document with ID '{doc_id}'
2. Analyze the content and rewrite it using proper Markdown formatting:
   - Use headers (# ## ###) for titles and sections
   - Use **bold** and *italic* for emphasis
   - Use bullet points or numbered lists where appropriate
   - Use code blocks (```) for any code snippets
   - Use blockquotes (>) for important callouts
   - Improve readability and structure
3. After reformatting, use the update_document tool to save the markdown version back to the document

Please proceed with these steps and show me the reformatted markdown content."""
        
        return GetPromptResult(
            description=f"Format document '{doc_id}' in Markdown syntax",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=prompt_text
                    )
                )
            ]
        )
    
    raise ValueError(f"Unknown prompt: {name}")

# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Run the MCP server via stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
    
