"""
Minimal MCP Server Test
"""
import asyncio
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent

server = Server("minimal-test")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="test_tool",
            description="A simple test tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "test_tool":
        msg = arguments.get("message", "")
        return [TextContent(type="text", text=f"Echo: {msg}")]
    return [TextContent(type="text", text="Unknown tool")]

if __name__ == "__main__":
    # Test without stdio first
    import sys
    print(f"Server name: {server.name}", file=sys.stderr)
    print(f"Capabilities: {server.get_capabilities()}", file=sys.stderr)
    print("Server initialized successfully", file=sys.stderr)
