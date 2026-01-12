# Re-ranking Quick Reference

## 🚀 Quick Start

### Run the demo:
```bash
python demo.py
# At prompt: /rerank-demo
```

### In your code:
```python
from anthropic import Anthropic
from hybrid_retriever import RetrieverWithReranking, chunk_text_by_section, generate_embeddings_batch

# Setup
client = Anthropic(api_key="your-api-key")
retriever = RetrieverWithReranking(client=client)

# Add documents
chunks = chunk_text_by_section(document_text)
embeddings = generate_embeddings_batch(chunks)
for chunk, embedding in zip(chunks, embeddings):
    retriever.add_document(chunk, embedding, {'content': chunk})

# Search with re-ranking
query_embedding = generate_embeddings_batch([query])[0]
results = retriever.search_with_reranking(query, query_embedding, top_k=3)

# Results are in Claude's preferred order
for metadata, score in results:
    print(metadata['content'])
```

## What It Does

**Before:** Hybrid search returns results based on:
- Vector similarity (semantic)
- BM25 score (keyword importance)
- RRF merge (balanced ranking)

❌ Problem: Still ranks by raw scores, not query intent

**After:** Claude re-ranks by:
- Understanding the actual query meaning
- Reading the document content
- Comparing relevance to specific query

✅ Solution: Results ranked by what Claude thinks is most relevant

## Example

Query: "What did the engineering team do with incident 2023?"

| Before | After |
|--------|-------|
| 1. Cybersecurity | 1. **Software Engineering** |
| 2. Software Engineering | 2. Cybersecurity |

Claude understands "engineering team" = Software Engineering section

## API Reference

### RetrieverWithReranking

```python
class RetrieverWithReranking(Retriever):
    def __init__(self, client: Optional[Anthropic] = None)
    def search_with_reranking(self, query: str, query_embedding: list, top_k: int = 3) -> list
```

**Parameters:**
- `client`: Anthropic client (required for re-ranking)
- `query`: Search query string
- `query_embedding`: Query embedding vector
- `top_k`: Number of results to return

**Returns:**
- List of `(metadata, score)` tuples in Claude's priority order

**Inheritance:**
- Inherits `add_document()`, `search()` from Retriever
- Inherits Vector + BM25 indexes
- Adds Claude re-ranking layer

## Trade-offs

| Factor | Value |
|--------|-------|
| Accuracy boost | ✅ Noticeable improvement |
| Speed impact | ⚠️ +1 API call (~1-2 seconds) |
| Cost | ⚠️ Extra Claude API tokens |
| Implementation | ✅ Simple (just use search_with_reranking) |

## When to Use

✅ Use for:
- Production RAG systems
- High-accuracy requirements
- Complex queries
- When accuracy > speed

❌ Skip for:
- Real-time systems
- Simple keyword searches
- Cost-constrained applications
- Streaming responses

## Testing

```bash
# Integration tests
python test_reranking_integration.py

# Pipeline tests
python test_reranking_pipeline.py

# Full verification
python verify_reranking.py
```

## Common Issues

**Issue:** "ANTHROPIC_API_KEY not set"
- Solution: Add to .env file: `ANTHROPIC_API_KEY=your-key`

**Issue:** RetrieverWithReranking "module not found"
- Solution: Make sure `hybrid_retriever.py` is in workspace

**Issue:** Demo shows "⚠️ ANTHROPIC_API_KEY not set"
- This is fine! Demo still works with hybrid search only
- Re-ranking step will use hybrid results as fallback

## Documentation

- **Full guide:** `HYBRID_RETRIEVER_README.md`
- **Implementation:** `RERANKING_IMPLEMENTATION.md`
- **Complete status:** `RERANKING_COMPLETE.md`

## Next Steps

1. Try `/rerank-demo` in demo.py
2. Integrate into your RAG pipeline
3. Compare accuracy vs latency trade-offs
4. Deploy to production with re-ranking

---

**Status:** ✅ Production Ready  
**Course:** Anthropic RAG Lesson 006  
**Files:** hybrid_retriever.py, demo.py
