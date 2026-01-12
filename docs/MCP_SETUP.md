# MCP Implementation Guide

Complete implementation of Model Context Protocol (MCP) with tools, resources, and prompts for document management integrated with Claude.

## Overview

This project demonstrates all three core MCP features:
1. **Tools** - Executable operations (read, update documents)
2. **Resources** - Static data access (list documents, fetch content)
3. **Prompts** - Pre-defined message templates (markdown formatting)

## Architecture

```
┌─────────────────┐
│   Claude API    │
└────────┬────────┘
         │
    Chat Messages + Tools
         │
┌────────▼──────────────────────┐
│   demo.py (MCP Client)         │
│  - Initializes MCP servers     │
│  - Discovers tools, resources  │
│  - Routes tool calls           │
│  - Fetches resources via @     │
│  - Executes prompts via /cmd   │
└────────┬──────────────────────┘
         │
     MCP Protocol (stdio)
         │
┌────────▼──────────────────────┐
│ document_server.py (MCP)       │
│  - Tools: read, update docs    │
│  - Resources: docs list, fetch │
│  - Prompts: format markdown    │
│  - In-memory storage           │
└────────────────────────────────┘
```

## MCP Features Implemented

### 1. Tools

**Definition** (document_server.py):
```python
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="read_document", ...),
        Tool(name="update_document", ...)
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "read_document":
        # Fetch document by name
    elif name == "update_document":
        # Update or create document
```

**Usage** (demo.py):
```python
# Tools are discovered at initialization
# Claude automatically calls them during conversation
# Tool execution is routed via execute_mcp_tool_fresh()
```

### 2. Resources

**Definition** (document_server.py):
```python
@server.resource("docs://documents", mime_type="application/json")
def list_docs():
    """Direct resource - returns JSON list of doc names"""
    return list(DOCUMENTS.keys())

@server.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id: str):
    """Templated resource - returns document content"""
    return DOCUMENTS[doc_id]
```

**Usage** (demo.py):
```python
# @mention syntax triggers resource fetching
# resolve_mentions_in_text() detects @document1, @kb-guide, etc.
# read_resource_async() calls session.read_resource(uri)
# Document content is injected into user message for context

User: "Tell me about @document1"
System fetches docs://documents/document1
Assistant receives document content in context
```

### 3. Prompts

**Definition** (document_server.py):
```python
@server.list_prompts()
async def list_prompts() -> list[dict]:
    return [
        {
            "name": "format",
            "description": "Rewrites the contents of a document in Markdown format",
            "arguments": [{"name": "doc_id", "description": "Document ID", "required": True}]
        }
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    if name == "format":
        # Well-tested, domain-specific prompt
        prompt_text = f"Please reformat document '{doc_id}' in markdown syntax..."
        return GetPromptResult(
            description="Format document in markdown",
            messages=[PromptMessage(role="user", content=prompt_text)]
        )
```

**Usage** (demo.py):
```python
# /format command triggers prompt execution
# execute_mcp_prompt() calls session.get_prompt()
# Prompt messages are sent to Claude with tools enabled

User: "/format document1"
System fetches format prompt with arguments
Claude receives pre-crafted prompt
Claude calls read_document and update_document tools
Result is reformatted markdown document
```

## Integration Points

### 1. MCP Server Initialization (demo.py)

```python
async def initialize_mcp_servers():
    for server_name, config in MCP_SERVERS_CONFIG.items():
        # Connect via stdio
        server_params = StdioServerParameters(command, args, env)
        session = ClientSession(stdio, write)
        await session.initialize()
        
        # Discover tools
        tools_response = await session.list_tools()
        for tool in tools_response.tools:
            mcp_tools.append(tool_dict)
        
        # Store session for later use
        mcp_sessions[server_name] = session
```

### 2. Tool Execution (demo.py)

```python
async def execute_mcp_tool_fresh(server_name, tool_name, arguments):
    # Create fresh connection for each tool call
    session = ClientSession(stdio, write)
    await session.initialize()
    
    # Call the tool
    result = await session.call_tool(tool_name, arguments)
    
    # Extract content and return
    return json.dumps({"result": content})
```

### 3. Resource Resolution (demo.py)

```python
async def read_resource_async(session, resource_uri: str) -> str:
    # Call session.read_resource(uri)
    result = await session.read_resource(resource_uri)
    
    # Parse MIME type
    if result[0].mime_type == "application/json":
        return result[0].text  # Return as-is (JSON)
    else:
        return result[0].text  # Return as text
```

### 4. Prompt Execution (demo.py)

```python
async def execute_mcp_prompt(server_name, prompt_name, arguments):
    # Create fresh connection
    session = ClientSession(stdio, write)
    
    # Get prompt from server
    result = await session.get_prompt(prompt_name, arguments)
    
    # Extract message text
    prompt_text = result.messages[0].content.text
    return prompt_text
```

## Configuration

### MCP Servers Config (demo.py)

```python
MCP_SERVERS_CONFIG = {
    "documents": {
        "command": sys.executable,
        "args": ["document_server.py"],
        "env": {}
    }
}
```

### Environment Variables (.env)

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Running the System

### Start the Demo

```powershell
.\.venv\Scripts\python demo.py
```

### Example Workflows

**Using Tools:**
```
User: What's the read_document tool for?
Assistant: The read_document tool lets me fetch document content by name...
```

**Using Resources via @mention:**
```
User: What's in @document1?
Assistant: Document1 contains OneSuite Core architecture overview...
```

**Using Prompts via /command:**
```
User: /format kb-guide
Assistant: I'll help you reformat the kb-guide document in markdown syntax...
[Calls read_document, reformats, calls update_document]
Result: Reformatted document in markdown
```

## Key Design Decisions

1. **Fresh connections per tool** - Avoids nested asyncio.run() conflicts
2. **Sync @mention resolver** - Uses execute_tool dispatcher instead of async
3. **Thread pool executor** - Manages async operations from sync context
4. **In-memory storage** - Simple document store for demos
5. **Comprehensive prompts** - Well-tested, production-ready instructions

## Testing

Test files in `tests/` directory:
- `test_mcp_direct.py` - Protocol-level MCP tests
- `test_resources_final.py` - Resource API validation
- `test_prompts.py` - Prompt delivery tests

## Future Enhancements

1. **Multiple MCP servers** - Add more specialized servers
2. **File-based storage** - Replace in-memory with persistent docs
3. **Authentication** - Add API keys to MCP servers
4. **Resource streaming** - Support large resource payloads
5. **Prompt parameters** - Dynamic prompt customization
6. **Error recovery** - Graceful handling of server failures

## Troubleshooting

### "Method not found" error
- Ensure MCP server is exposing the right decorators
- Check that `@server.list_tools()` or `@server.list_resources()` exists
- Verify stdio transport is working

### Tool not discovered
- Check `initialize_mcp_servers()` is called
- Verify tool is returned by `list_tools()`
- Check tool schema has required fields

### Resource not found
- Verify resource URI matches `@server.resource()` decorator
- Check templated resource pattern is correct
- Ensure resource handler returns proper type

### Prompt not executing
- Check `@server.get_prompt()` is implemented
- Verify prompt returns `GetPromptResult` with messages
- Ensure prompt message has role and content

---

**Status:** All three MCP features (tools, resources, prompts) fully implemented and integrated
**Last Updated:** January 2026
