# Context for Claude Computer Use

## My Multi-Agent System Overview

I have a multi-agent system with 3 autonomous agents built in Python:

### 1. MCP Document Server Agent
- **Location**: `C:\Users\farismai2\coding\training\src\document_server.py`
- **Purpose**: Model Context Protocol server for document management
- **Tools Provided**:
  - `document_path_to_markdown`: Converts PDF/DOCX to Markdown
  - `list_documents`: Lists available documents
  - `read_document`: Reads document contents
- **Logging**: Structured JSON logging to `logs/document_server.log`

### 2. Production Monitoring Agent
- **Location**: `.github/workflows/auto-fix-errors.yml` + `scripts/auto_fix_errors.py`
- **Purpose**: Runs daily at 6 AM UTC to analyze production logs and auto-fix bugs
- **Capabilities**:
  - Reads logs from `logs/` directory
  - Uses Claude Sonnet 4 to analyze errors
  - Generates fix code and explanations
  - Creates GitHub pull requests with fixes
- **API**: Uses Anthropic API with `claude-sonnet-4-20250514`

### 3. Computer Use QA Agent (Current)
- **Location**: `computer-use/scripts/` directory
- **Purpose**: Automated UI/UX testing using Computer Use API
- **Test App**: `computer-use/test-app/index.html` (@mention component with bugs)
- **Custom Client**: `computer-use/scripts/computer_use_client.py`

## Project Structure

```
C:\Users\farismai2\coding\training\
├── src/
│   ├── document_server.py       # MCP server
│   ├── document_utils.py        # PDF/DOCX conversion
│   └── logging_config.py        # Structured logging
├── tests/
│   └── test_document_conversion.py  # TDD test suite (5/5 passing)
├── scripts/
│   └── auto_fix_errors.py       # Production monitor agent
├── computer-use/
│   ├── scripts/
│   │   ├── computer_use_client.py    # Custom Python client
│   │   └── qa_test_mention_component.py  # QA test script
│   ├── test-app/
│   │   └── index.html           # Test web app with bugs
│   ├── launch-reference-ui.bat  # Windows launcher (currently running)
│   └── README.md                # Computer Use setup guide
├── logs/                        # Application logs (JSON format)
├── .github/workflows/           # GitHub Actions
└── .claude/commands/            # Custom Claude commands (WorkTrees)
```

## Current Testing Focus

### @Mention Component Bugs (in test-app/index.html)

**Known Issues:**
1. **Bug 1**: Autocomplete position is wrong after backspace when 2+ mentions exist
2. **Bug 2**: Autocomplete doesn't close properly in some scenarios
3. **Bug 3**: Escape key doesn't always work to dismiss autocomplete

**Test Scenarios:**
```
1. Type "@" - autocomplete should appear
2. Type "@john" - autocomplete should filter
3. Press Enter - should insert mention pill
4. Type "@alice" - add second mention
5. Press Backspace after second mention - CHECK POSITION (bug here!)
6. Press Escape - autocomplete should disappear
```

## How to Test My Application

### Option 1: Test the @Mention Component
```bash
# In the Computer Use environment:
1. Navigate to: C:\Users\farismai2\coding\training\computer-use\test-app
2. Open index.html in browser (or use: python -m http.server 8000)
3. Test the @mention component following the scenarios above
4. Report bugs found with screenshots
```

### Option 2: Test the MCP Server
```bash
# Start the MCP server first (in a separate terminal):
cd C:\Users\farismai2\coding\training
python start_document_server.py

# Then test document conversion:
# Place a PDF/DOCX in the test-data/ directory
# Use the document_path_to_markdown tool
```

## API Keys & Configuration

- **Anthropic API Key**: Already configured in environment
- **Model**: Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- **Git Branch**: `claude/import-vs-workspace-kobAs`
- **Repository**: https://github.com/farismai27/training

## Development Workflow

I use **Git WorkTrees** for parallel development:
- Custom commands: `/create-worktree`, `/merge-worktree`, `/cleanup-worktrees`
- Located in: `.claude/commands/`

## Documentation Available

- `WHAT_YOU_BUILT.md` - Complete system overview
- `COMPUTER_USE.md` - 100+ Computer Use examples
- `REFERENCE_UI_GUIDE.md` - This UI's guide (20+ pages)
- `PRODUCTION_MONITORING.md` - Production monitor setup
- `PARALLEL_DEVELOPMENT.md` - Git WorkTrees guide
- `MCP_SERVER_SETUP.md` - MCP server configuration

---

## Quick Start Commands

**For you (Claude) to use:**

```bash
# Navigate to my project
cd C:/Users/farismai2/coding/training

# List project structure
dir

# Open test app in browser
cd computer-use/test-app
python -m http.server 8000
# Then navigate to: http://localhost:8000

# Check test results
pytest tests/ -v

# View logs
type logs\document_server.log
```

## What I Need Help With

I want you to:
1. **Test the @mention component** and verify the 3 known bugs
2. **Provide detailed bug reports** with screenshots
3. **Suggest fixes** for each bug
4. Help me understand **how Computer Use works** behind the scenes

You have full access to my Windows machine. Feel free to:
- Navigate the file system
- Open browsers and applications
- Run Python scripts
- Edit code files
- Take screenshots for bug documentation

---

**System Context**: You are running in the Anthropic Computer Use Reference Implementation with access to a virtual Ubuntu desktop. You can control the mouse, keyboard, and see the screen. My actual project files are at the Windows path above, but you're running in a containerized Linux environment with access to browser tools.
