# Project Overview

OCAA (OneSuite Core Architect Agent) is a unified multi-agent system combining product strategy, QA automation, error monitoring, and workflow execution capabilities.

## What is OCAA?

OCAA is an AI-powered assistant designed specifically for OneSuite Core development, combining multiple specialized agents into a single cohesive system:

```
┌─────────────────────────────────────────────────────────┐
│                    OCAA Web UI                          │
│              (Streamlit Interface)                      │
└────────────────────┬────────────────────────────────────┘
                     │
            ┌────────┴────────┐
            │  Unified Agent  │
            │  (Orchestrator) │
            └────────┬────────┘
                     │
      ┌──────────────┼──────────────┬──────────────┐
      │              │              │              │
┌─────▼─────┐  ┌────▼────┐  ┌──────▼──────┐  ┌───▼────┐
│ RAG Agent │  │Computer │  │  Production │  │Workflow│
│           │  │   Use   │  │   Monitor   │  │ Engine │
│ • Hybrid  │  │ • QA    │  │  • Errors   │  │ • Eval │
│ • Rerank  │  │ • Tests │  │  • Auto-fix │  │ • Opt  │
└───────────┘  └─────────┘  └─────────────┘  └────────┘
```

## Core Capabilities

### 1. Product Strategy 📝
Define and document product features for OneSuite Core.

- **User Story Development** - Create clear, actionable user stories
- **Acceptance Criteria** - Define measurable success criteria
- **Multi-Channel Analysis** - Impact across Search, Social, Programmatic, Commerce
- **Roadmap Planning** - Strategic product planning

**Example:**
```
User: "Write a user story for advanced search filtering"
OCAA: Creates comprehensive user story with:
  - Context & Problem Statement
  - Solution Overview
  - Acceptance Criteria (Given/When/Then)
  - Channel Impact Analysis
  - Dependencies & Constraints
```

### 2. QA Testing & Automation 🧪
Automated testing using Computer Use capabilities.

- **UI/UX Testing** - Screenshot analysis and validation
- **Interaction Automation** - Mouse & keyboard automation
- **Test Execution** - Run test suites automatically
- **Report Generation** - PASS/FAIL with evidence

**Example:**
```
User: "Test the @mention component"
OCAA:
  1. Takes screenshot of current state
  2. Types '@' and validates autocomplete appears
  3. Tests Enter key to insert mention
  4. Validates styling and behavior
  5. Generates test report with results
```

### 3. Production Monitoring 🔍
Analyze production errors and generate fixes.

- **Log Analysis** - Parse production logs for errors
- **Root Cause Analysis** - Understand why errors occur
- **Auto-Fix Generation** - Propose code fixes
- **Prevention Strategies** - Avoid future errors

**Example:**
```
User: "Analyze this error: TypeError: Cannot read property 'id' of undefined"
OCAA:
  - Identifies null/undefined object access
  - Suggests null-checking pattern
  - Provides code fix
  - Recommends TypeScript strict mode
```

### 4. Workflow Execution 🔄
Design and execute complex AI workflows.

- **Evaluator-Optimizer Patterns** - Producer → Grader → Feedback loop
- **RAG Pipelines** - Retrieval → Re-ranking → Generation
- **Multi-Step Automation** - Chain multiple operations
- **Iterative Refinement** - Quality improvement loops

**Example:**
```
User: "Write a product requirement document"
OCAA:
  1. Producer: Writes initial draft
  2. Grader: Evaluates quality (1-10)
  3. Feedback: Provides improvement suggestions
  4. Refine: Iterates until quality threshold met
  5. Delivers: Final polished document
```

## Architecture Stack

### Frontend
- **Streamlit** - Web UI framework
- **Python 3.11+** - Core language
- **Custom CSS** - OneSuite branding

### AI & ML
- **Claude API** - Anthropic's Claude models
  - Sonnet 4 (default) - Balanced performance
  - Opus 4 (optional) - Maximum capability
  - Haiku (optional) - Speed-optimized
- **Sentence Transformers** - Embeddings for RAG
- **BM25** - Lexical search

### Automation
- **PyAutoGUI** - Mouse & keyboard control
- **PIL/Pillow** - Screenshot & image analysis
- **Playwright** (optional) - Browser automation

### Document Processing
- **PDFPlumber** - PDF extraction
- **python-docx** - Word document processing
- **Markdown** - Document formatting

### Data & Storage
- **JSON** - Conversation storage
- **Local Files** - Knowledge bases
- **In-Memory** - Session state

## Key Components

### 1. Unified Agent (`src/demo_unified.py`)
Main orchestrator combining all capabilities.

**Features:**
- 15+ commands (`/hybrid-demo`, `/qa-test`, `/monitor-errors`)
- Multi-agent coordination
- Streaming responses
- Tool use integration

**Size:** 150 KB, 4,147 lines

### 2. RAG Agent (`src/demo.py`)
Retrieval-augmented generation specialist.

**Features:**
- Hybrid search (semantic + lexical)
- Claude-powered re-ranking
- MCP server integration
- Knowledge base management

**Size:** 132 KB

### 3. Computer Use Agent (`computer-use/scripts/`)
Browser automation and QA testing.

**Features:**
- Screenshot analysis
- Test automation
- Visual validation
- Report generation

**Size:** ~40 KB across multiple files

### 4. Document Server (`src/document_server.py`)
MCP protocol server for document management.

**Features:**
- Document indexing
- Semantic search
- Format conversion
- Tool integration

**Size:** 11 KB

### 5. Web UI (`ocaa_web_ui.py`)
Streamlit-based user interface.

**Features:**
- Chat interface
- Quick action buttons
- Conversation history
- API key management

**Size:** 16 KB

## Tech Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **AI Models** | Claude Sonnet 4 | Core intelligence |
| **Framework** | Streamlit | Web UI |
| **Language** | Python 3.11+ | Core language |
| **RAG** | Sentence-BERT + BM25 | Hybrid retrieval |
| **Automation** | PyAutoGUI, PIL | Computer use |
| **Documents** | PDFPlumber, python-docx | Document processing |
| **Protocol** | MCP | Model Context Protocol |
| **API** | Anthropic Messages API | Claude integration |

## Project Structure

```
training/
├── src/                       # Source code
│   ├── demo_unified.py       # ⭐ Unified agent (150 KB)
│   ├── demo.py               # RAG agent (132 KB)
│   ├── document_server.py    # MCP server
│   ├── hybrid_retriever.py   # Hybrid search
│   ├── document_utils.py     # Doc conversion
│   └── logging_config.py     # Logging setup
│
├── computer-use/             # QA automation
│   ├── scripts/              # Automation scripts
│   ├── docker/               # Docker setup
│   └── test-app/             # Test applications
│
├── docs/                     # 📚 Documentation
│   ├── 01-getting-started/   # Setup guides
│   ├── 02-architecture/      # System design
│   ├── 03-features/          # Feature guides
│   └── ...                   # Other sections
│
├── tests/                    # Test suite
├── data/                     # Test data
├── knowledge/                # Knowledge bases
├── rag/                      # RAG implementations
├── scripts/                  # Automation scripts
│   └── auto_fix_errors.py    # Auto-fix agent
│
├── ocaa_web_ui.py           # 🌐 Web UI (16 KB)
├── requirements.txt          # Dependencies
└── .env.example              # Config template
```

## Design Principles

### 1. Unified Interface
Single agent combining multiple specialized capabilities.

**Why:** Simplifies user experience, reduces context switching.

### 2. Modular Architecture
Each capability is independently implementable and testable.

**Why:** Maintainability, scalability, and clear separation of concerns.

### 3. Context Preservation
Conversation history maintained across agent interactions.

**Why:** Better understanding of user intent and continuity.

### 4. Production-Ready
Logging, error handling, and monitoring built-in.

**Why:** Reliable operation in production environments.

### 5. OneSuite-First
Specialized for OneSuite Core product development.

**Why:** Deep domain knowledge and tailored workflows.

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| **Response Time** | 2-5s | Simple queries |
| **Response Time** | 5-15s | Complex workflows |
| **Memory Usage** | ~200 MB | Base system |
| **Memory Usage** | ~500 MB | With Computer Use |
| **Concurrent Users** | 10+ | Streamlit default |
| **Max Tokens** | 4096 | Configurable |

## Deployment Options

### Local Development
```bash
streamlit run ocaa_web_ui.py
```
**Use for:** Development, testing, personal use

### Production (Single User)
```bash
streamlit run ocaa_web_ui.py --server.headless=true --server.port=8501
```
**Use for:** Personal production deployment

### Production (Multi-User)
```bash
streamlit run ocaa_web_ui.py --server.headless=true --server.port=8501 --server.maxUploadSize=10
```
**Use for:** Team deployments

### Docker (Future)
```bash
docker-compose up
```
**Use for:** Isolated environments, cloud deployment

## Next Steps

Now that you understand OCAA's architecture:

1. ✅ [Quick Start](./quick-start.md) - Run your first agent
2. ✅ [Common Tasks](./common-tasks.md) - Learn frequent workflows
3. ✅ [Architecture Deep Dive](../02-architecture/overview.md) - System internals
4. ✅ [Feature Guides](../03-features/overview.md) - Specific capabilities

## Resources

- **Live Demo**: `streamlit run ocaa_web_ui.py`
- **Architecture**: [System Overview](../02-architecture/overview.md)
- **API Reference**: [Claude API](../05-api/claude-api.md)
- **Examples**: See [Features](../03-features/overview.md)

---

**Updated:** 2026-01-18
**Next:** [Quick Start](./quick-start.md)
