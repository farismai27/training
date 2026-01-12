# RAG (Retrieval Augmented Generation) - Quick Start Guide

## 🎯 What You Need to Know

RAG solves the problem of asking Claude questions about large documents by:
1. Breaking documents into chunks
2. Finding relevant chunks for each question
3. Only including relevant chunks in the prompt

## 📚 Learning Path

### Step 1: Understand the Basics (15 min)
**File:** `rag_demo.py`

Run this first to see the core concept:
```bash
python rag_demo.py
```

**What it shows:**
- ❌ Option 1: Putting entire document in prompt (simple but limited)
- ✅ Option 2: RAG with chunking (scalable and efficient)
- Comparison showing 50%+ prompt size reduction

**Key Insight:** RAG is essential for documents over ~10k tokens

---

### Step 2: Production Techniques (30 min)
**File:** `rag_advanced.py`

**Install dependencies:**
```bash
pip install sentence-transformers numpy
```

**Run it:**
```bash
python rag_advanced.py
```

**What you'll learn:**
- Semantic search with embeddings (not just keywords)
- Different chunking strategies
- Vector-based retrieval (cosine similarity)
- Hybrid retrieval (keyword + semantic)

**Key Insight:** Embeddings understand meaning, not just word matches

---

### Step 3: Real-World Files (45 min)
**File:** `rag_practical.py`

**Install file handlers:**
```bash
pip install pypdf2 python-docx sentence-transformers numpy
```

**Run it:**
```bash
python rag_practical.py
```

**What you'll learn:**
- Loading PDF, DOCX, TXT files
- Saving/loading embeddings (avoid recomputing)
- Multi-document search
- Production workflow

**Key Insight:** Preprocess once, query many times

---

## 🚀 Quick Start - Copy & Paste

### Basic RAG (Keyword-based)
```python
from rag_demo import option2_rag

document = "Your large document text here..."
question = "What are the risk factors?"
answer, chunks = option2_rag(document, question, top_k=3)
print(answer)
```

### Advanced RAG (Embeddings)
```python
from rag_advanced import RAGPipeline, SemanticSectionChunking, VectorRetriever

# Setup
pipeline = RAGPipeline(SemanticSectionChunking, VectorRetriever())
pipeline.index_document(your_document)

# Query
answer, chunks = pipeline.query("Your question?", top_k=3)
print(answer)
```

### Production RAG (Persistent)
```python
from rag_practical import PersistentRAG

# First time: Process and save
rag = PersistentRAG()
rag.add_document("./myfile.pdf")
rag.chunk_documents(chunk_size=500)
rag.create_embeddings()
rag.save_index("my_docs")

# Later: Just load and query
rag = PersistentRAG()
rag.load_index("my_docs")
answer = rag.query("Your question?")
```

---

## 💡 When to Use What?

### Use Simple Approach (Option 1)
- ✅ Document < 10k tokens
- ✅ Need to analyze entire document
- ✅ Speed/simplicity more important than cost

### Use Basic RAG (rag_demo.py)
- ✅ Quick prototype
- ✅ No extra dependencies
- ✅ Keyword search is sufficient

### Use Advanced RAG (rag_advanced.py)
- ✅ Need semantic understanding
- ✅ Questions use synonyms/paraphrasing
- ✅ Better retrieval accuracy matters

### Use Production RAG (rag_practical.py)
- ✅ Multiple documents
- ✅ Repeated queries on same documents
- ✅ Need to handle PDFs/DOCX
- ✅ Production deployment

---

## 🔧 Tuning Guide

### Chunking Parameters

**chunk_size**: How big each chunk is
- **Small (200-300 chars)**: Precise but may miss context
- **Medium (500-700 chars)**: Good balance
- **Large (1000+ chars)**: More context but less precise

**overlap**: Prevents splitting related content
- Typical: 10-20% of chunk_size
- Example: chunk_size=500, overlap=50

**Strategy**:
- **Semantic**: Best for structured docs (reports, articles)
- **Fixed-size**: Works for any text
- **Sentence**: Natural boundaries

### Retrieval Parameters

**top_k**: How many chunks to retrieve
- **Few (1-2)**: Fast, cheap, focused
- **Medium (3-5)**: Balanced
- **Many (6+)**: More context but costly

**Retrieval method**:
- **Keyword**: Fast, simple, free
- **Semantic**: Better accuracy, needs embeddings
- **Hybrid**: Best of both worlds

---

## 🎓 Anthropic Course Concepts

### The Two Options

**Option 1: Full Document**
```
User Question + Entire Document → Claude → Answer
```
- Simple but limited
- Expensive for large docs
- May exceed token limits

**Option 2: RAG**
```
Step 1 (Preprocessing): Document → Chunks → Store
Step 2 (Query): User Question → Find Relevant Chunks → Claude → Answer
```
- Scalable to huge documents
- Cheaper and faster
- Requires more engineering

### RAG Trade-offs

**✅ Advantages:**
- Scales to 100-1000+ page documents
- Multiple documents supported
- Smaller prompts = faster + cheaper
- Focuses Claude on relevant content

**⚠️ Challenges:**
- More complex to implement
- Requires preprocessing
- Need to choose chunking strategy
- Need retrieval mechanism
- May miss context if wrong chunks selected

---

## 📊 Performance Comparison

From `rag_demo.py` output:

| Approach | Prompt Size | Cost | Speed | Accuracy |
|----------|-------------|------|-------|----------|
| Full Doc | ~2700 chars | High | Slower | Good |
| RAG | ~1350 chars | Low | Faster | Good |
| **Reduction** | **50%** | **50%** | **2x** | **Same** |

For a 1000-page document:
- Full Doc: May exceed limits ❌
- RAG: Works perfectly ✅

---

## 🏗️ Production Stack

### Embeddings
- **OpenAI**: `text-embedding-3-small` (best)
- **Sentence Transformers**: `all-MiniLM-L6-v2` (free, good)
- **Cohere**: `embed-english-v3.0`

### Vector Databases
- **Pinecone**: Managed, easy ($)
- **Weaviate**: Open source, powerful
- **Chroma**: Simple, embedded DB
- **FAISS**: Fast, in-memory

### Framework
- **LangChain**: Full RAG pipeline
- **LlamaIndex**: Document-focused
- **Custom**: Like our examples (more control)

---

## ❓ Common Questions

**Q: When should I use RAG vs full document?**
A: Use RAG when document > 10k tokens OR you have multiple documents

**Q: Which chunking strategy is best?**
A: Semantic for structured docs, fixed-size for general text

**Q: Keyword or semantic retrieval?**
A: Semantic is better but requires embeddings. Start with keyword, upgrade if needed.

**Q: How do I evaluate if my RAG is working?**
A: Check if retrieved chunks contain answer, test with known questions

**Q: What if RAG retrieves wrong chunks?**
A: Increase top_k, improve chunking, or use hybrid retrieval

**Q: How much does it cost?**
A: RAG reduces Claude costs by 50%+. Embeddings cost ~$0.01 per 10k chunks (one-time)

---

## 🎯 Next Steps

1. ✅ Run all three demo files
2. 📝 Try with your own documents
3. 🧪 Experiment with chunking strategies
4. 📊 Measure retrieval accuracy
5. 🚀 Deploy to production with vector DB

## 📖 Resources

- **This course**: Anthropic RAG Module
- **Docs**: `RAG_README.md` (detailed guide)
- **Files**: 
  - `rag_demo.py` - Basic concepts
  - `rag_advanced.py` - Advanced techniques
  - `rag_practical.py` - Production examples

---

## 💾 Files Created

```
training/
├── rag_demo.py              # Start here - basic RAG
├── rag_advanced.py          # Embeddings & strategies
├── rag_practical.py         # Real files & persistence
├── RAG_README.md            # Full documentation
└── RAG_QUICKSTART.md        # This file
```

Happy learning! 🎉
