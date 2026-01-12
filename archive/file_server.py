"""
File Operations MCP Server
Provides tools to read, write, list, and delete files in allowed directories.
"""
import asyncio
import sys
from pathlib import Path
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Allowed directories (configure as needed)
ALLOWED_PATHS = [
    str(Path.home() / "Documents"),
    str(Path.home() / "Downloads"),
    str(Path(__file__).parent)  # Current project directory
]

def is_path_allowed(filepath: str) -> bool:
    """Check if filepath is within allowed directories."""
    try:
        abs_path = str(Path(filepath).resolve())
        return any(abs_path.startswith(allowed) for allowed in ALLOWED_PATHS)
    except Exception:
        return False

# Create MCP server
server = Server("file-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available file operation tools."""
    return [
        Tool(
            name="read_file",
            description=f"Read contents of a text file. Allowed paths: {', '.join(ALLOWED_PATHS)}",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Absolute or relative path to the file"
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="write_file",
            description=f"Write or create a text file. Allowed paths: {', '.join(ALLOWED_PATHS)}",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Absolute or relative path to the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["filepath", "content"]
            }
        ),
        Tool(
            name="list_files",
            description=f"List files in a directory. Allowed paths: {', '.join(ALLOWED_PATHS)}",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory path to list files from"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Optional glob pattern (e.g., '*.txt', '*.py')"
                    }
                },
                "required": ["directory"]
            }
        ),
        Tool(
            name="delete_file",
            description=f"Delete a file. Allowed paths: {', '.join(ALLOWED_PATHS)}",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file to delete"
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="file_info",
            description="Get information about a file (size, modified date, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file"
                    }
                },
                "required": ["filepath"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a file operation tool."""
    
    if name == "read_file":
        filepath = arguments.get("filepath", "")
        
        if not is_path_allowed(filepath):
            return [TextContent(
                type="text",
                text=f"Error: Access denied. Path not in allowed directories."
            )]
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return [TextContent(
                type="text",
                text=f"File: {filepath}\n\n{content}"
            )]
        except FileNotFoundError:
            return [TextContent(type="text", text=f"Error: File not found: {filepath}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error reading file: {str(e)}")]
    
    elif name == "write_file":
        filepath = arguments.get("filepath", "")
        content = arguments.get("content", "")
        
        if not is_path_allowed(filepath):
            return [TextContent(
                type="text",
                text=f"Error: Access denied. Path not in allowed directories."
            )]
        
        try:
            # Create parent directories if they don't exist
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return [TextContent(
                type="text",
                text=f"Successfully wrote {len(content)} characters to {filepath}"
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error writing file: {str(e)}")]
    
    elif name == "list_files":
        directory = arguments.get("directory", "")
        pattern = arguments.get("pattern", "*")
        
        if not is_path_allowed(directory):
            return [TextContent(
                type="text",
                text=f"Error: Access denied. Path not in allowed directories."
            )]
        
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return [TextContent(type="text", text=f"Error: Directory not found: {directory}")]
            
            if not dir_path.is_dir():
                return [TextContent(type="text", text=f"Error: Not a directory: {directory}")]
            
            files = list(dir_path.glob(pattern))
            
            if not files:
                return [TextContent(type="text", text=f"No files matching '{pattern}' in {directory}")]
            
            file_list = []
            for f in sorted(files):
                size = f.stat().st_size if f.is_file() else "DIR"
                file_list.append(f"{f.name} ({size} bytes)" if size != "DIR" else f"{f.name} (DIR)")
            
            return [TextContent(
                type="text",
                text=f"Files in {directory}:\n" + "\n".join(file_list)
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error listing files: {str(e)}")]
    
    elif name == "delete_file":
        filepath = arguments.get("filepath", "")
        
        if not is_path_allowed(filepath):
            return [TextContent(
                type="text",
                text=f"Error: Access denied. Path not in allowed directories."
            )]
        
        try:
            Path(filepath).unlink()
            return [TextContent(type="text", text=f"Successfully deleted {filepath}")]
        except FileNotFoundError:
            return [TextContent(type="text", text=f"Error: File not found: {filepath}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error deleting file: {str(e)}")]
    
    elif name == "file_info":
        filepath = arguments.get("filepath", "")
        
        if not is_path_allowed(filepath):
            return [TextContent(
                type="text",
                text=f"Error: Access denied. Path not in allowed directories."
            )]
        
        try:
            path = Path(filepath)
            if not path.exists():
                return [TextContent(type="text", text=f"Error: File not found: {filepath}")]
            
            stat = path.stat()
            info = [
                f"Path: {filepath}",
                f"Size: {stat.st_size} bytes",
                f"Type: {'Directory' if path.is_dir() else 'File'}",
                f"Modified: {stat.st_mtime}",
                f"Created: {stat.st_ctime}"
            ]
            
            return [TextContent(type="text", text="\n".join(info))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error getting file info: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

async def main():
    """Run the MCP server using stdio transport."""
    import mcp.server.stdio
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        from mcp.server import NotificationOptions
        
        init_options = InitializationOptions(
            server_name="file-server",
            server_version="1.0.0",
            capabilities=server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={}
            )
        )
        
        await server.run(
            read_stream,
            write_stream,
            init_options,
            raise_exceptions=False
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        raise
