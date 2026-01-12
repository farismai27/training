# RAG & MCP Agent Training

A comprehensive implementation of RAG (Retrieval-Augmented Generation) systems from the Anthropic course, combined with MCP (Model Context Protocol) integration for Claude agents.

## 📁 Project Structure

```
training/
├── src/                                    # Main source code
│   ├── demo.py                            # Main Claude agent (use this!)
│   ├── document_server.py                 # MCP server with resources
│   ├── hybrid_retriever.py                # RAG retrieval system
│   └── extract_pdf.py                     # PDF extraction utility
│
├── rag/                                   # RAG implementations (Anthropic course)
│   ├── rag_demo.py                       # Start here: Basic RAG
│   ├── rag_workflow_demo.py              # 5-step RAG workflow
│   ├── rag_advanced.py                   # Production techniques
│   ├── rag_practical.py                  # Real-world usage
│   └── rag_visual.py                     # Visual learning
│
├── data/                                  # Data and documents
│   ├── report.md                         # Test document for demos
│   ├── dataset.json                      # Sample test data
│   ├── pm_dataset.json                   # Product data
│   ├── pdf_content.txt                   # Extracted PDF content
│   └── OneSuite-Platform User Stories-*.pdf
│
├── knowledge/                             # Knowledge bases
│   └── onesuite_user_stories.md          # 51 user stories KB
│
├── notebooks/                             # Jupyter notebooks
│   └── 005_hybrid_retrieval.ipynb        # Interactive hybrid search demo
│
├── tests/                                 # Comprehensive test suite
│   ├── test_hybrid_retriever.py          # Hybrid search tests
│   ├── test_reranking_integration.py     # Re-ranking integration
│   ├── test_reranking_pipeline.py        # Full pipeline tests
│   ├── verify_reranking.py               # Verification script
│   └── ... (other tests)
│
├── docs/                                  # Documentation
│   ├── HYBRID_RETRIEVER_README.md        # Hybrid search guide
│   ├── RERANKING_QUICK_REFERENCE.md      # Re-ranking quick start
│   ├── RERANKING_IMPLEMENTATION.md       # Implementation details
│   ├── RERANKING_COMPLETE.md             # Complete status
│   ├── IMPLEMENTATION_CHECKLIST.md       # Full checklist
│   ├── RAG_README.md                     # RAG overview
│   ├── RAG_QUICKSTART.md                 # Quick start guide
│   ├── RAG_COMPLETE_SUMMARY.md           # Complete summary
│   ├── RAG_CHECKLIST.md                  # RAG checklist
│   ├── RAG_INDEX.md                      # RAG index
│   ├── MCP_SETUP.md                      # MCP integration
│   └── ... (other docs)
│
├── .env                                   # API keys (git ignored)
├── .env.example                          # Environment template
├── requirements.txt                      # Python dependencies
└── README.md                             # This file
```

## 🚀 Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
```

### 2. Run the Main Agent
```bash
python src/demo.py
```

Available commands:
- `/hybrid-demo` - See semantic + lexical search comparison
- `/rerank-demo` - See Claude-powered re-ranking
- `/rag-demo` - See 5-step RAG workflow
- `/mcp-tools` - List available tools

### 3. Run Tests
```bash
# Integration tests
python tests/test_reranking_integration.py

# Full verification
python tests/verify_reranking.py
```

## 📚 Learning Path (Anthropic Course)

### Lesson 003: Vector Embeddings
- **Concept:** Semantic search using embeddings
- **Status:** ✅ Implemented
- **Files:** `src/hybrid_retriever.py` (SimpleVectorIndex)
- **Demo:** `/hybrid-demo` → "SEMANTIC SEARCH ONLY"

### Lesson 004: BM25 & Lexical Search
- **Concept:** Keyword-based search with IDF weighting
- **Status:** ✅ Implemented
- **Files:** `src/hybrid_retriever.py` (BM25Index)
- **Demo:** `/hybrid-demo` → "LEXICAL SEARCH (BM25)"

### Lesson 005: Hybrid Retrieval
- **Concept:** Combine semantic + lexical via Reciprocal Rank Fusion
- **Status:** ✅ Implemented
- **Files:** `src/hybrid_retriever.py` (Retriever)
- **Demo:** `/hybrid-demo` → "HYBRID SEARCH (RRF)"
- **Notebook:** `notebooks/005_hybrid_retrieval.ipynb`

### Lesson 006: Re-ranking with Claude
- **Concept:** Use Claude to understand query intent and reorder results
- **Status:** ✅ Implemented
- **Files:** `src/hybrid_retriever.py` (RetrieverWithReranking)
- **Demo:** `/rerank-demo`
- **Quick Ref:** `docs/RERANKING_QUICK_REFERENCE.md`

## 🔄 RAG Pipeline

The complete pipeline implemented:

```
1. Load Document
   ↓
2. Chunk by Section
   ↓
3. Generate Embeddings
   ↓
4. Hybrid Search (Vector + BM25 + RRF)
   ↓
5. Re-rank with Claude
   ↓
6. Add Context to Prompt
   ↓
7. Send to Claude
   ↓
8. Get Answer
```

See `/rag-demo` in demo.py for full example.

## 📖 Documentation

### For Learning
- **RAG Fundamentals:** `docs/RAG_README.md`
- **Quick Start:** `docs/RAG_QUICKSTART.md`
- **Complete Summary:** `docs/RAG_COMPLETE_SUMMARY.md`

### For Implementation
- **Hybrid Search:** `docs/HYBRID_RETRIEVER_README.md`
- **Re-ranking:** `docs/RERANKING_QUICK_REFERENCE.md`
- **Full Details:** `docs/RERANKING_IMPLEMENTATION.md`

### For Configuration
- **MCP Setup:** `docs/MCP_SETUP.md`

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Integration tests (quick)
python tests/test_reranking_integration.py
# Expected: 4/4 tests passing

# Full verification
python tests/verify_reranking.py
# Expected: 7/7 checks passing

# Pipeline tests
python tests/test_reranking_pipeline.py
```

## 🎯 Key Features

### Hybrid Retrieval System
- **Vector Index:** Semantic search via cosine similarity
- **BM25 Index:** Lexical search with term weighting
- **RRF Merger:** Balanced combination of both
- **Re-ranking:** Claude enhances relevance

### MCP Integration
- **Resources:** Access documents via `docs://documents/*`
- **Tools:** List, read, update documents
- **Prompts:** Format documents with context

### Knowledge Bases
- **OneSuite User Stories:** 51 platform-specific stories
- **Access:** Via agent KB, MCP resources, or files

## 📊 Implementation Status

| Component | Status | Tests | Docs |
|-----------|--------|-------|------|
| Vector Search | ✅ Complete | ✅ Pass | ✅ Yes |
| BM25 Search | ✅ Complete | ✅ Pass | ✅ Yes |
| Hybrid Merger | ✅ Complete | ✅ Pass | ✅ Yes |
| Re-ranking | ✅ Complete | ✅ Pass | ✅ Yes |
| MCP Server | ✅ Complete | ✅ Pass | ✅ Yes |
| Agent Integration | ✅ Complete | ✅ Pass | ✅ Yes |

## 🔧 Configuration

### Environment Variables
```bash
ANTHROPIC_API_KEY=sk-...              # Required for Claude API
CONFLUENCE_URL=...                    # Optional for Confluence
CONFLUENCE_EMAIL=...                  # Optional for Confluence
CONFLUENCE_API_TOKEN=...              # Optional for Confluence
```

### Python Requirements
```
anthropic>=0.39.0
sentence-transformers>=2.2.0
python-dotenv>=1.0.0
rank-bm25>=0.2.3
```

See `requirements.txt` for complete list.

## 🚦 Troubleshooting

**Issue:** "report.md not found"
- **Solution:** Make sure `data/report.md` exists
- **Alternative:** Create test document in `data/` folder

**Issue:** "ANTHROPIC_API_KEY not set"
- **Solution:** Add to `.env` file
- **Create:** `cp .env.example .env` then edit

**Issue:** "hybrid_retriever module not found"
- **Solution:** Import from `src` folder
- **Check:** `sys.path.insert(0, "src")`

## 📝 Examples

### Use Hybrid Retrieval
```python
from src.hybrid_retriever import Retriever, chunk_text_by_section, generate_embeddings_batch

# Load and prepare
chunks = chunk_text_by_section(document_text)
embeddings = generate_embeddings_batch(chunks)

# Create retriever
retriever = Retriever()
for chunk, embedding in zip(chunks, embeddings):
    retriever.add_document(chunk, embedding, {'content': chunk})

# Search
query_embedding = generate_embeddings_batch([query])[0]
results = retriever.search(query, query_embedding, top_k=3)
```

### Use Re-ranking
```python
from anthropic import Anthropic
from src.hybrid_retriever import RetrieverWithReranking

# Create retriever with re-ranking
client = Anthropic(api_key="your-key")
retriever = RetrieverWithReranking(client=client)

# Add documents (same as above)
...

# Search with re-ranking
results = retriever.search_with_reranking(query, embedding, top_k=3)
```

## 📚 References

- **Anthropic RAG Course:** https://www.anthropic.com
- **RAG Papers:** Check `docs/` folder
- **MCP Docs:** https://modelcontextprotocol.io

## 🎓 What You'll Learn

After using this codebase, you'll understand:
- ✅ How embeddings work for semantic search
- ✅ BM25 algorithm for lexical search
- ✅ Merging search results via RRF
- ✅ Claude-powered re-ranking for accuracy
- ✅ Building production RAG systems
- ✅ MCP integration with agents
- ✅ Testing retrieval pipelines

## 📄 License

Educational material for learning RAG concepts.

## 🤝 Support

For issues or questions:
1. Check `docs/` folder for detailed guides
2. Review test files for examples
3. Run verification: `python tests/verify_reranking.py`

---

**Last Updated:** January 12, 2026
**Status:** ✅ Production Ready
**Course:** Anthropic RAG Fundamentals (Lessons 003-006)
