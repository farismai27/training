# MCP Server Setup Guide

This guide shows you how to connect your custom MCP server to Claude Code, enabling Claude to use your `document_path_to_markdown` tool.

## What You've Built

You now have a fully functional MCP server with a custom tool that converts PDF and Word documents to Markdown format!

**Tool Available:**
- `document_path_to_markdown` - Converts PDF (.pdf) or Word (.docx) files to Markdown

## Setup Instructions

### Option 1: Using Claude Code CLI (Recommended)

If you have Claude Code installed on your machine:

```bash
# Navigate to your project directory
cd C:\Users\farismai2\coding

# Add the MCP server to Claude Code
clod mcp add documents "python start_document_server.py"
```

**What this does:**
- `clod mcp add` - Command to add an MCP server
- `documents` - Name for your server (can be anything you want)
- `"python start_document_server.py"` - Command to start your server

### Option 2: Manual Configuration

Add this to your Claude Code configuration file (usually at `~/.config/claude/claude_desktop_config.json` or similar):

```json
{
  "mcpServers": {
    "documents": {
      "command": "python",
      "args": ["C:/Users/farismai2/coding/start_document_server.py"]
    }
  }
}
```

## Testing Your MCP Server

### 1. Start Claude Code

```bash
clod
```

### 2. Test the Document Conversion Tool

Ask Claude to convert a document:

```
Convert the contents of tests/fixtures/mcp_demo.docx to Markdown
```

Claude will automatically:
1. Detect your MCP server
2. Use the `document_path_to_markdown` tool
3. Read and convert the document
4. Show you the Markdown output

### 3. Try with Your Own Files

You can now ask Claude to convert any PDF or Word document:

```
Convert the file at C:\Users\farismai2\Documents\report.pdf to Markdown
```

## Available Tools

Your MCP server provides these tools to Claude:

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `read_document` | Read a document from memory | `name` (string) |
| `update_document` | Create/update a document in memory | `name` (string), `content` (string) |
| `document_path_to_markdown` | Convert PDF/Word to Markdown | `file_path` (string) |

## Demo Files

Test files are available in `tests/fixtures/`:
- `mcp_demo.docx` - Sample Word document about MCP

## Troubleshooting

**Server won't start?**
- Make sure dependencies are installed: `pip install -r requirements.txt`
- Check that Python can find the src directory
- Verify the path to `start_document_server.py` is correct

**Tool not working?**
- Ensure file paths are absolute or relative to the correct directory
- Verify PDF/Word documents exist at the specified path
- Check that pdfplumber and python-docx are installed

**Connection issues?**
- Restart Claude Code after adding the server
- Check Claude Code logs for error messages
- Verify the server starts without errors: `python start_document_server.py`

## Expanding Your MCP Server

You can add more tools to enhance Claude's capabilities:

### Ideas for Additional Tools:

1. **Image Analysis**
   - Extract text from images (OCR)
   - Analyze image content

2. **File Operations**
   - Search files by content
   - Create file summaries

3. **External APIs**
   - GitHub integration (read issues, PRs)
   - Jira integration (ticket management)
   - Slack integration (send messages)

4. **Data Processing**
   - CSV/Excel parsing
   - JSON manipulation
   - Data visualization

### Adding a New Tool

1. **Define the tool in `src/document_server.py`:**
   ```python
   Tool(
       name="your_tool_name",
       description="What your tool does",
       inputSchema={...}
   )
   ```

2. **Implement the handler in `call_tool()`:**
   ```python
   elif name == "your_tool_name":
       # Your implementation
       return [TextContent(...)]
   ```

3. **Write tests in `tests/`:**
   ```python
   def test_your_tool():
       result = your_tool(args)
       assert result == expected
   ```

4. **Commit and enjoy!**

## Next Steps

1. ✅ Test the document conversion with your own files
2. ✅ Explore adding more custom tools
3. ✅ Share your MCP server with your team
4. ✅ Check out [Model Context Protocol docs](https://modelcontextprotocol.io)

## Real-World Use Cases

### Development Workflow Enhancement

- **Sentry Integration**: Fetch production errors directly in Claude
- **Jira/GitHub**: Read and create tickets/issues
- **Slack**: Get notified when tasks complete
- **Documentation**: Auto-convert docs between formats

### Data Analysis

- **PDF Reports**: Extract and analyze report data
- **Word Documents**: Process business documents
- **Spreadsheets**: Parse and summarize data

### Content Management

- **Markdown Generation**: Convert various formats to Markdown
- **Document Processing**: Batch process multiple files
- **Text Extraction**: Pull specific information from documents

---

**Congratulations!** 🎉

You've successfully:
- ✅ Built a custom MCP tool using TDD
- ✅ Integrated it with your MCP server
- ✅ Set it up for use with Claude Code
- ✅ Tested it with real documents

Claude can now read and convert your PDF and Word documents automatically!
