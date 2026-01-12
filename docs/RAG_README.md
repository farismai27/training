# RAG (Retrieval Augmented Generation) Learning Module

Based on the Anthropic Course lesson on RAG techniques.

## What is RAG?

RAG is a technique for working with large documents by:
1. **Chunking**: Breaking documents into smaller pieces
2. **Retrieval**: Finding the most relevant chunks for a question
3. **Generation**: Using only relevant chunks in the prompt to Claude

## Files in This Module

### 1. `rag_demo.py` - Basic RAG Concepts
**Start here!** This demonstrates the core concepts from the course:

- **Option 1**: Putting entire document in prompt (simple but limited)
- **Option 2**: RAG with chunking + retrieval (scalable)
- Side-by-side comparison showing trade-offs
- Simple keyword-based retrieval

**Run it:**
```bash
python rag_demo.py
```

**What you'll learn:**
- Why RAG is needed for large documents
- How chunking works (section-based splitting)
- Basic keyword retrieval
- Prompt size reduction benefits

### 2. `rag_advanced.py` - Production RAG Techniques
**Next level!** Shows production-grade RAG implementation:

- Multiple chunking strategies (semantic, fixed-size, sentence-based)
- Semantic retrieval with embeddings (not just keywords)
- Hybrid retrieval (keyword + semantic)
- Comparison of different approaches

**Setup:**
```bash
pip install sentence-transformers numpy
```

**Run it:**
```bash
python rag_advanced.py
```

**What you'll learn:**
- How to use embeddings for semantic search
- Different chunking strategies and when to use them
- Vector-based retrieval (cosine similarity)
- Hybrid retrieval combining multiple methods

## Quick Start

### 1. Run Basic Demo (No extra dependencies)
```bash
python rag_demo.py
```

This will show you:
- Full document vs RAG approach
- How chunks are created
- Which chunks are retrieved
- Answer quality comparison
- Prompt size reduction

### 2. Try Advanced Examples (Requires sentence-transformers)
```bash
pip install sentence-transformers numpy
python rag_advanced.py
```

This will demonstrate:
- Semantic search with embeddings
- Comparison of chunking strategies
- Comparison of retrieval methods

## Key Concepts from the Course

### When to Use RAG

✅ **Use RAG when:**
- Document is very large (100-1000+ pages)
- Working with multiple documents
- Need to reduce costs (smaller prompts)
- Need faster responses
- Document exceeds Claude's context window

❌ **Avoid RAG when:**
- Document is small (<10k tokens)
- Need to analyze entire document holistically
- Simplicity is more important than optimization

### RAG Trade-offs

**Advantages:**
- ✅ Scales to very large documents
- ✅ Reduces prompt size → faster + cheaper
- ✅ Focuses Claude's attention on relevant content
- ✅ Works with multiple documents

**Challenges:**
- ⚠️ More complex implementation
- ⚠️ Requires preprocessing step
- ⚠️ Need to choose chunking strategy
- ⚠️ Need search/retrieval mechanism
- ⚠️ May miss context if wrong chunks selected

## Production RAG Stack

In real applications, you'd typically use:

### Embedding Models
- OpenAI: `text-embedding-ada-002`, `text-embedding-3-small`
- Open source: `sentence-transformers` models
- Cohere: `embed-english-v3.0`

### Vector Databases
- **Pinecone**: Managed, easy to use
- **Weaviate**: Open source, feature-rich
- **Chroma**: Simple, embedded database
- **FAISS**: Facebook's similarity search library
- **Qdrant**: High-performance vector search

### Advanced Techniques
- **Reranking**: Re-score retrieved chunks for better relevance
- **Hybrid Search**: Combine keyword + semantic search
- **Metadata Filtering**: Filter by date, source, category, etc.
- **Parent-Child Documents**: Retrieve small chunks, include larger context
- **Query Expansion**: Rephrase query for better retrieval

## Examples Walkthrough

### Example 1: Basic RAG
```python
from rag_demo import compare_approaches

# This will show both Option 1 (full doc) and Option 2 (RAG)
compare_approaches("What risk factors does this company have?")
```

### Example 2: Advanced with Embeddings
```python
from rag_advanced import RAGPipeline, SemanticSectionChunking, VectorRetriever

# Create pipeline
pipeline = RAGPipeline(SemanticSectionChunking, VectorRetriever())

# Index your document
pipeline.index_document(your_document_text)

# Query
answer, retrieved_chunks = pipeline.query("Your question here", top_k=3)
print(answer)
```

## Tuning Parameters

### Chunking
- **chunk_size**: 200-1000 chars (balance context vs precision)
- **overlap**: 10-20% of chunk_size (prevent splitting related content)
- **strategy**: Semantic > Fixed-size > Sentence (depends on document structure)

### Retrieval
- **top_k**: 2-5 chunks (more = more context but longer prompts)
- **alpha** (hybrid): 0.5-0.8 (weight for semantic vs keyword)

### Testing
Evaluate your RAG system on:
1. **Retrieval accuracy**: Are the right chunks retrieved?
2. **Answer quality**: Does Claude give good answers?
3. **Cost**: How many tokens per query?
4. **Latency**: How long does it take?

## Next Steps

1. ✅ Run `rag_demo.py` to understand basics
2. ✅ Install sentence-transformers and run `rag_advanced.py`
3. 📝 Try with your own documents
4. 🔧 Experiment with different chunking strategies
5. 🎯 Compare retrieval methods for your use case
6. 🚀 Consider adding vector database for production

## Resources

- Anthropic Course: RAG Module
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- [Pinecone Learning Center](https://www.pinecone.io/learn/)

## Common Issues

### "Document too large" error
→ Use RAG! Your document exceeds Claude's context window.

### Retrieved chunks don't contain answer
→ Try increasing `top_k` or improving chunking strategy

### Answers are too generic
→ Retrieved chunks may lack context. Try larger chunks or overlap.

### Slow performance
→ Use vector database instead of computing embeddings every time

### Low retrieval accuracy
→ Try hybrid retrieval or better embedding model
