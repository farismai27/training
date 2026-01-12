# Hybrid Retrieval System - Complete Implementation

This directory now includes a complete implementation of the hybrid retrieval system from the Anthropic RAG course, combining semantic search and lexical search using Reciprocal Rank Fusion.

## Files Added

### 1. `hybrid_retriever.py`
The core implementation module containing:

#### Classes:
- **`SimpleVectorIndex`** - Semantic search using cosine similarity
  - `add_document(embedding, metadata)` - Store embeddings
  - `search(query_embedding, top_k)` - Find similar chunks
  
- **`BM25Index`** - Lexical search using BM25 algorithm
  - `add_document(text, metadata)` - Index text for keyword search
  - `search(query, top_k)` - Find relevant chunks by keywords
  - Uses term frequency and inverse document frequency
  
- **`Retriever`** - Hybrid system combining both search methods
  - `add_document(text, embedding, metadata)` - Add to both indexes
  - `search(query, query_embedding, top_k)` - Search both, merge with RRF
  - `_reciprocal_rank_fusion(results_list, k)` - Merge rankings

#### Helper Functions:
- `generate_embeddings_batch(texts)` - Create embeddings via sentence-transformers
- `chunk_text_by_section(text)` - Split markdown by headers

### 2. `005_hybrid_retrieval.ipynb`
Jupyter notebook demonstrating:
- Loading and chunking documents
- Generating embeddings
- Building the hybrid retriever
- Testing semantic search alone
- Testing lexical (BM25) search alone
- Testing hybrid search with RRF
- Understanding the math behind RRF

### 3. Updated `demo.py`
Added command `/hybrid-demo` to the agent:
- New function `run_hybrid_retriever_demo()`
- Integration with knowledge base
- Help menu updated

## The Problem This Solves

**Semantic Search Alone Has Limitations:**

Query: "What happened with incident 2023 Q4 011"

❌ Vector Index Results:
1. Section 10 (Cybersecurity) ✅ Correct
2. Section 3 (Financial Analysis) ❌ Wrong - doesn't mention the incident

The vector similarity found Section 3 similar overall, but missed that this section doesn't contain the critical keyword "incident 2023".

**The Solution: Hybrid Search**

✅ Hybrid Results (via RRF):
1. Section 10 (Cybersecurity) ✅ High in both systems
2. Section 2 (Software Engineering) ✅ High in both systems
3. Section 5 (Methodology) - Lower priority

## How It Works

### Step 1: Semantic Search (Vector Index)
- Create embeddings for all chunks
- Calculate cosine similarity between query and chunks
- Rank by similarity score

### Step 2: Lexical Search (BM25)
- Tokenize query into words
- Calculate term frequency across documents
- Weight by inverse document frequency (rare terms = important)
- Rank by BM25 relevance score

### Step 3: Reciprocal Rank Fusion (RRF)
Merge results using the formula:

```
RRF_score = sum(1 / (k + rank)) for all ranking systems
```

Where:
- `k` = constant (typically 60)
- `rank` = position in each search system (1st, 2nd, 3rd, etc.)

**Example:**

Semantic rankings: [A, B, C]
BM25 rankings: [C, A, B]

RRF Scores:
- A: 1/(60+1) + 1/(60+2) = 0.0324 ⭐ Best (high in both)
- C: 1/(60+3) + 1/(60+1) = 0.0321 (mixed)
- B: 1/(60+2) + 1/(60+3) = 0.0317 (mixed)

Final Ranking: **A > C > B**

## Usage

### In Demo Agent

```bash
python demo.py
```

Then at the prompt:
```
You: /hybrid-demo
```

This will:
1. Load report.md
2. Create embeddings
3. Build hybrid retriever
4. Show semantic results
5. Show BM25 results
6. Show hybrid results with RRF
7. Explain the math and differences

### In Your Code

```python
from hybrid_retriever import Retriever, chunk_text_by_section, generate_embeddings_batch

# Load and chunk document
with open('report.md') as f:
    text = f.read()
chunks = chunk_text_by_section(text)

# Generate embeddings
embeddings = generate_embeddings_batch(chunks)

# Build retriever
retriever = Retriever()
for chunk, embedding in zip(chunks, embeddings):
    metadata = {'content': chunk}
    retriever.add_document(chunk, embedding, metadata)

# Search
query_embedding = generate_embeddings_batch(['your query'])[0]
results = retriever.search('your query', query_embedding, top_k=3)

for metadata, score in results:
    print(f"Score: {-score:.4f}")
    print(f"Content: {metadata['content']}")
```

## Extending the Retriever

The beauty of the Retriever pattern is extensibility. Add any search method as long as it has the same API:

```python
class MyCustomSearch:
    def add_document(self, text, metadata):
        # Your implementation
        pass
    
    def search(self, query, top_k):
        # Return [(metadata, distance), ...] 
        pass

# Add to retriever
retriever.custom_search = MyCustomSearch()
retriever._reciprocal_rank_fusion([
    semantic_results,
    bm25_results,
    custom_results  # Automatically included!
])
```

## Key Concepts

| Concept | Definition | Purpose |
|---------|-----------|---------|
| **Semantic Search** | Uses embeddings and vector similarity | Understand meaning and context |
| **Lexical Search** | Uses keywords and term frequency | Find exact matches and important terms |
| **BM25** | Best Match 25 algorithm | Rank documents by keyword relevance |
| **Reciprocal Rank Fusion** | Combine rankings from multiple systems | Balance multiple ranking approaches |
| **IDF** | Inverse Document Frequency | Weight rare terms higher |

## Math Deep Dive

### Cosine Similarity (Vector Index)
```
similarity = dot_product(A, B) / (magnitude(A) × magnitude(B))
distance = 1 - similarity
```

### BM25 Score (Lexical Search)
```
score = sum( IDF(term) × (term_freq × (k1 + 1)) / (term_freq + k1 × (1 - b + b × norm_length)) )

where:
- IDF(term) = log((N - df + 0.5) / (df + 0.5) + 1)
- N = total documents
- df = documents containing term
- k1 = saturation parameter (1.5)
- b = length normalization (0.75)
```

### Reciprocal Rank Fusion
```
RRF = sum(1 / (k + rank_i)) for all ranking systems
```

## Dependencies

- `sentence-transformers` (optional, for real embeddings)
- `numpy` (if using real embeddings)
- Python 3.8+

If sentence-transformers is not installed, uses simulated embeddings for demo purposes.

## Next Steps in RAG

After hybrid retrieval, the full RAG pipeline continues:
1. ✅ Chunk document
2. ✅ Generate embeddings  
3. ✅ Search (hybrid)
4. ✅ Re-rank results (Claude refinement)
5. ➡️ Add context to prompt
6. ➡️ Send to Claude
7. ➡️ Claude generates answer

The hybrid retriever ensures steps 3-4 return the most relevant context for steps 5-7.

## Advanced: Re-ranking with Claude

While hybrid search (Lesson 005) combines semantic and lexical approaches, it still has limitations:

**Example Problem:**
Query: "What did the **engineering team** do with incident 2023?"

Hybrid Result (before re-ranking):
1. Cybersecurity (high in both semantic and BM25)
2. Software Engineering (medium in both)

**Better Result (after Claude re-ranking):**
1. Software Engineering (Claude understands "engineering team" = Software Engineering)
2. Cybersecurity (supporting context)

### RetrieverWithReranking Class

Added to `hybrid_retriever.py`:

```python
from anthropic import Anthropic
from hybrid_retriever import RetrieverWithReranking

# Create retriever with re-ranking
client = Anthropic(api_key="your-api-key")
retriever = RetrieverWithReranking(client=client)

# Add documents (same as regular Retriever)
for chunk, embedding in zip(chunks, embeddings):
    metadata = {'content': chunk, 'section': chunk.split('\n')[0]}
    retriever.add_document(chunk, embedding, metadata)

# Search with re-ranking
results = retriever.search_with_reranking(
    query="What did the engineering team do?",
    query_embedding=query_embedding,
    top_k=3
)
```

### How It Works

1. **Hybrid Search** - Get initial top-k results (Vector + BM25 + RRF)
2. **Format Results** - Convert to XML with document IDs
3. **Claude Re-ranking** - Send query + documents to Claude
4. **Parse Response** - Extract Claude's priority ordering
5. **Return** - Documents in Claude's order of relevance

### When to Use Re-ranking

**Use re-ranking when:**
- ✅ Query understanding is critical (complex, multi-concept queries)
- ✅ Accuracy is more important than latency
- ✅ You're building production RAG systems
- ✅ Your hybrid search results need refinement

**Don't use re-ranking when:**
- ❌ Low latency required
- ❌ Token budget is limited
- ❌ Simple, straightforward queries
- ❌ Cost optimization needed

### Trade-offs

| Aspect | Hybrid | Hybrid + Re-ranking |
|--------|--------|---------------------|
| Accuracy | Good | Better ⭐ |
| Latency | Fast | Slower (extra API call) |
| Cost | Cheaper | More expensive (Claude call) |
| Complexity | Medium | Higher |
| Best For | General use | High-accuracy systems |

### In Demo Agent

```bash
python demo.py
```

Then at the prompt:
```
You: /rerank-demo
```

This will demonstrate:
- Basic query with re-ranking
- Complex query with multiple concepts
- Before/after comparison
- Explanation of improvements

## References

- **Course:** Anthropic RAG course (006 Re-ranking)
- **Technique:** Learned-to-rank with LLM
- **Papers:** "Improve RAG with Re-ranking" (Anthropic)

---

**Status:** ✅ Complete implementation with demo and notebook
**Last Updated:** January 12, 2026
