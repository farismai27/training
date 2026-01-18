# Features Overview

Complete guide to OCAA's capabilities and features.

## Feature Categories

OCAA combines multiple specialized capabilities into a unified system:

```
┌──────────────────────────────────────────────────────────┐
│                    OCAA Features                         │
└──────────────────────────────────────────────────────────┘
           │
           ├─ 🤖 Agents
           │  ├─ Unified Agent (All capabilities)
           │  ├─ RAG Agent (Hybrid retrieval + re-ranking)
           │  ├─ Computer Use Agent (QA automation)
           │  └─ Production Monitor (Error analysis)
           │
           ├─ 🌐 Web UI
           │  ├─ Chat Interface
           │  ├─ Quick Actions
           │  └─ Conversation History
           │
           ├─ 🔍 RAG System
           │  ├─ Hybrid Retrieval (Semantic + Lexical)
           │  ├─ Re-ranking (Claude-powered)
           │  └─ Document Server (MCP)
           │
           ├─ 🔄 Workflows
           │  ├─ Evaluator-Optimizer
           │  ├─ Producer-Grader
           │  └─ Multi-step Automation
           │
           └─ 🛠️ Tools
              ├─ Computer Use (Screenshots, automation)
              ├─ Document Processing (PDF, DOCX, MD)
              └─ Git Worktrees (Parallel development)
```

---

## 🤖 Agents

### Unified Agent
**The all-in-one OCAA experience.**

**File:** `src/demo_unified.py` (150 KB)

**Capabilities:**
- ✅ Product strategy and user stories
- ✅ QA testing with Computer Use
- ✅ Error monitoring and auto-fix
- ✅ RAG workflows
- ✅ Multi-step automation

**Commands:**
```
/hybrid-demo       - Hybrid search demo
/rerank-demo       - Re-ranking demo
/qa-test <url>     - Run QA tests
/monitor-errors    - Analyze logs
/workflow-demo     - Evaluator-Optimizer demo
/full-automation   - Run all capabilities
```

**Use when:** You want all OCAA capabilities in one agent

[→ Full Guide](./agents/unified-agent.md)

---

### RAG Agent
**Specialized retrieval-augmented generation.**

**File:** `src/demo.py` (132 KB)

**Capabilities:**
- ✅ Hybrid search (semantic + BM25)
- ✅ Claude-powered re-ranking
- ✅ MCP server integration
- ✅ Knowledge base management
- ✅ Contextual retrieval

**Commands:**
```
/rag-demo          - Full RAG pipeline
/contextual-demo   - Contextual retrieval
/hybrid-demo       - Hybrid search
/rerank-demo       - Re-ranking
/mcp-tools         - List MCP tools
```

**Use when:** You need advanced search and retrieval

[→ Full Guide](./agents/rag-agent.md)

---

### Computer Use Agent
**Automated QA testing and browser automation.**

**File:** `computer-use/scripts/unified_agent.py` (23 KB)

**Capabilities:**
- ✅ Screenshot capture and analysis
- ✅ Mouse and keyboard automation
- ✅ Visual validation
- ✅ Test report generation
- ✅ Multi-step test scenarios

**Example:**
```python
# Test @mention component
python computer-use/scripts/qa_test_mention_component.py

# Custom test
python computer-use/run-unified-agent.py
```

**Use when:** You need automated UI testing

[→ Full Guide](./agents/computer-use.md)

---

### Production Monitor
**Error analysis and automated bug fixing.**

**File:** `scripts/auto_fix_errors.py` (350 lines)

**Capabilities:**
- ✅ Log file analysis
- ✅ Error pattern detection
- ✅ Root cause analysis
- ✅ Fix generation with code
- ✅ GitHub PR creation

**Example:**
```python
# Analyze logs
python scripts/auto_fix_errors.py

# Run via GitHub Actions
# Automatically runs on schedule or push
```

**Use when:** You need production error monitoring

[→ Full Guide](./agents/production-monitor.md)

---

## 🌐 Web UI

### Chat Interface
**Beautiful Streamlit-based UI for OCAA.**

**File:** `ocaa_web_ui.py` (16 KB)

**Features:**
- ✅ Real-time chat with Claude
- ✅ Conversation history
- ✅ Message streaming
- ✅ API key management
- ✅ Export conversations

**Components:**
- Chat area with message history
- User and assistant messages
- Markdown rendering
- Code syntax highlighting

**Launch:**
```bash
streamlit run ocaa_web_ui.py
```

[→ Full Guide](./web-ui/overview.md)

---

### Quick Actions
**Pre-built prompts for common tasks.**

**Features:**
- 📝 Generate Product Roadmap
- ✍️ Write User Story
- 🧪 QA Test @Mention
- 🐛 Analyze Error
- 🔄 Workflow Demo

**How it works:**
1. Click button in sidebar
2. Pre-configured prompt is sent
3. OCAA responds with specialized output
4. Continue conversation if needed

**Customization:**
Add new quick actions by editing `ocaa_web_ui.py`:
```python
if st.button("My Custom Action", key="custom_btn"):
    st.session_state.quick_action = "Your custom prompt here"
```

[→ Full Guide](./web-ui/quick-actions.md)

---

### Conversation Management
**Save, export, and manage conversations.**

**Features:**
- 🗑️ Clear conversation
- 💾 Export to JSON
- 📊 Conversation statistics
- 🔄 Session persistence

**Export format:**
```json
{
  "timestamp": "2026-01-18T10:30:00",
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

---

## 🔍 RAG System

### Hybrid Retrieval
**Combine semantic and lexical search.**

**Algorithm:**
```
1. Semantic Search (Sentence-BERT embeddings)
   - Understands meaning
   - Finds conceptually similar content

2. Lexical Search (BM25)
   - Keyword matching
   - Finds exact term matches

3. Fusion (Reciprocal Rank Fusion)
   - Combines both rankings
   - Best of both worlds
```

**Performance:**
- Recall: 90%+ (finds relevant content)
- Precision: 85%+ (results are relevant)
- Speed: <100ms for 1000 documents

[→ Full Guide](./rag/hybrid-retrieval.md)

---

### Re-ranking with Claude
**Use Claude to re-order search results.**

**Process:**
```
Search Results → Claude Analysis → Re-ranked Results

Input:  [Doc 1, Doc 2, Doc 3, Doc 4, Doc 5]
          ↓
Claude: "Which documents best answer the query?"
          ↓
Output: [Doc 3, Doc 1, Doc 5, Doc 2, Doc 4]
        (sorted by relevance)
```

**Benefits:**
- Improved relevance (10-15% better)
- Context-aware ranking
- Query understanding
- Multi-hop reasoning

**Cost:**
- ~1000 tokens per re-ranking
- $0.01-0.02 per query (Sonnet)

[→ Full Guide](./rag/reranking.md)

---

### Document Server (MCP)
**Model Context Protocol server for documents.**

**Capabilities:**
- Index documents
- Semantic search
- Format conversion
- Tool integration

**Protocol:**
```
Client → MCP Server → Documents
  |
  └─ Tools:
     - list_documents
     - search_documents
     - get_document
     - format_document
```

**Supported formats:**
- Markdown (.md)
- PDF (.pdf)
- Word (.docx)
- Text (.txt)

[→ Full Guide](./rag/document-server.md)

---

## 🔄 Workflows

### Evaluator-Optimizer Pattern
**Iterative quality improvement.**

**Pattern:**
```
┌──────────┐    ┌─────────┐    ┌──────────┐
│ Producer │ → │ Grader  │ → │ Feedback │
│ (Create) │   │ (Score) │   │ (Improve)│
└──────────┘    └─────────┘    └──────────┘
      ↑                              │
      └──────── Loop until ──────────┘
                quality met
```

**Example:**
```python
# Write product requirement
1. Producer: Creates initial draft
2. Grader: Scores quality (1-10)
3. Feedback: Suggests improvements
4. Producer: Refines based on feedback
5. Repeat until score ≥ 8
```

**Applications:**
- Document writing
- Code generation
- Test case creation
- Product specs

[→ Full Guide](./workflows.md)

---

### Multi-Step Automation
**Chain multiple operations.**

**Example:**
```python
# Full automation workflow
/full-automation

1. QA Testing
   - Launch test app
   - Run test suite
   - Generate report

2. Error Monitoring
   - Analyze logs
   - Identify errors
   - Generate fixes

3. Workflow Demo
   - Producer-Grader loop
   - Quality validation
   - Final output
```

---

## 🛠️ Tools

### Computer Use
**Screenshot, mouse, keyboard automation.**

**Capabilities:**
- 📸 Take screenshots
- 🖱️ Move mouse, click
- ⌨️ Type text
- 👁️ Analyze visuals
- ✅ Validate UI state

**Requirements:**
```bash
pip install pillow pyautogui
```

**Example:**
```python
# Take screenshot
screenshot = pyautogui.screenshot()

# Click at position
pyautogui.click(x=100, y=200)

# Type text
pyautogui.typewrite("Hello World")
```

[→ Full Guide](./computer-use.md)

---

### Document Processing
**Convert between document formats.**

**Supported:**
- PDF → Text
- DOCX → Markdown
- Markdown → HTML
- Text → Structured data

**Example:**
```python
from src.document_utils import convert_document

# Convert PDF to text
text = convert_document("report.pdf", output_format="text")

# Convert DOCX to Markdown
markdown = convert_document("doc.docx", output_format="markdown")
```

[→ Full Guide](./documents.md)

---

### Git Worktrees
**Parallel development workflows.**

**Commands:**
```bash
# Create worktree
/create-worktree feature-name

# Merge worktree
/merge-worktree feature-name

# Cleanup worktrees
/cleanup-worktrees
```

**Benefits:**
- Work on multiple features simultaneously
- No branch switching
- Isolated workspaces
- Easy merging

[→ Full Guide](../07-workflows/worktrees.md)

---

## Feature Comparison

| Feature | Unified | RAG | Computer Use | Web UI |
|---------|---------|-----|--------------|--------|
| Product Strategy | ✅ | ❌ | ❌ | ✅ |
| Hybrid Search | ✅ | ✅ | ❌ | ✅ |
| Re-ranking | ✅ | ✅ | ❌ | ✅ |
| QA Testing | ✅ | ❌ | ✅ | ✅* |
| Error Monitoring | ✅ | ❌ | ❌ | ✅ |
| Workflows | ✅ | ❌ | ❌ | ✅ |
| MCP Server | ❌ | ✅ | ❌ | ❌ |
| CLI Interface | ✅ | ✅ | ✅ | ❌ |
| Web Interface | ❌ | ❌ | ❌ | ✅ |

*Via Unified Agent

---

## Next Steps

- **Learn specific features**: Browse feature-specific guides
- **Understand architecture**: [Architecture Overview](../02-architecture/overview.md)
- **Start developing**: [Development Guide](../04-development/coding-standards.md)
- **Deploy to production**: [Deployment Guide](../06-deployment/production.md)

---

**Updated:** 2026-01-18
**Total Features:** 15+
