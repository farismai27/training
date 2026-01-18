# Setup Guide

Get your OCAA development environment up and running.

## Prerequisites

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Anthropic API Key** - [Get API Key](https://console.anthropic.com/)

## Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/farismai27/training.git
cd training
```

### 2. Install Dependencies

**For Web UI (Recommended):**
```bash
pip install -r requirements_ocaa_ui.txt
```

**For Full System (All Features):**
```bash
pip install -r requirements.txt
```

**Core Dependencies Only:**
```bash
pip install anthropic streamlit python-dotenv
```

### 3. Configure API Key

**Option A: Environment Variable (Recommended)**
```bash
# Linux/Mac
export ANTHROPIC_API_KEY='your-api-key-here'

# Windows PowerShell
$env:ANTHROPIC_API_KEY = "your-api-key-here"

# Windows CMD
set ANTHROPIC_API_KEY=your-api-key-here
```

**Option B: .env File**
```bash
# Create .env file
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

**Option C: Enter in Web UI**
- Launch the UI and enter your API key in the sidebar

### 4. Launch OCAA

**Web UI (Easiest):**
```bash
# Windows
.\launch_ocaa_ui.bat

# Linux/Mac
./launch_ocaa_ui.sh

# Or directly
streamlit run ocaa_web_ui.py
```

**Unified Agent (CLI):**
```bash
python src/demo_unified.py
```

**Original RAG Agent:**
```bash
python src/demo.py
```

## Verify Installation

### Test Web UI
1. Open browser to http://localhost:8501
2. You should see "OCAA - OneSuite Core Architect Agent"
3. Enter your API key if not set
4. Try typing a message: "What can you help me with?"

### Test CLI Agent
```bash
python src/demo_unified.py
# Type: /hybrid-demo
# Expected: RAG search demo runs successfully
```

## Common Issues

### Issue: `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```bash
pip install streamlit
```

### Issue: `ModuleNotFoundError: No module named 'anthropic'`

**Solution:**
```bash
pip install anthropic
```

### Issue: API Key Not Working

**Check:**
1. Key is valid: https://console.anthropic.com/
2. Key has correct permissions
3. No extra spaces or quotes in the key

**Test:**
```python
import anthropic
client = anthropic.Anthropic(api_key="your-key")
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.content[0].text)
```

### Issue: Port 8501 Already in Use

**Solution:**
```bash
# Find process using port 8501
lsof -i :8501  # Mac/Linux
netstat -ano | findstr :8501  # Windows

# Kill the process or use different port
streamlit run ocaa_web_ui.py --server.port 8502
```

### Issue: Computer Use Features Not Working

**Solution:**
```bash
# Install optional dependencies
pip install pillow pyautogui pdfplumber python-docx
```

## Development Setup

For development work:

```bash
# Install all dependencies including dev tools
pip install -r requirements.txt

# Install testing dependencies
pip install pytest pytest-asyncio

# Install linting tools
pip install ruff black mypy
```

## Directory Structure After Setup

```
training/
├── src/                    # Source code
│   ├── demo.py            # RAG agent
│   ├── demo_unified.py    # Unified agent
│   └── document_server.py # MCP server
├── docs/                  # Documentation
├── tests/                 # Test suite
├── data/                  # Test data
├── knowledge/             # Knowledge bases
├── ocaa_web_ui.py        # Web UI
├── requirements.txt       # Python dependencies
└── .env                   # API keys (create this)
```

## Next Steps

- ✅ [Project Overview](./project-overview.md) - Understand the architecture
- ✅ [Quick Start](./quick-start.md) - Run your first agent
- ✅ [Common Tasks](./common-tasks.md) - Learn frequent workflows
- ✅ [Web UI Guide](../03-features/web-ui/overview.md) - Master the web interface

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude |
| `OPENAI_API_KEY` | No | OpenAI API key (for embeddings) |
| `LOG_LEVEL` | No | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `STREAMLIT_SERVER_PORT` | No | Custom port for Streamlit (default: 8501) |

## Platform-Specific Notes

### Windows
- Use PowerShell or CMD
- Run `.\launch_ocaa_ui.bat` for easy startup
- Backslashes in file paths: `C:\Users\...`

### macOS
- Use Terminal or iTerm
- Run `./launch_ocaa_ui.sh`
- May need to run: `chmod +x launch_ocaa_ui.sh`

### Linux
- Use bash or zsh
- Run `./launch_ocaa_ui.sh`
- May need to install system dependencies:
  ```bash
  sudo apt-get update
  sudo apt-get install python3-pip python3-dev
  ```

## Troubleshooting

Still having issues? Check:

1. **Python version**: `python --version` (should be 3.11+)
2. **Pip version**: `pip --version`
3. **API key**: Valid and active
4. **Network**: Can reach api.anthropic.com
5. **Logs**: Check `/tmp/streamlit.log` or console output

For more help, see [FAQ](../08-reference/faq.md).

---

**Updated:** 2026-01-18
**Next:** [Project Overview](./project-overview.md)
