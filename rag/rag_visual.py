"""
Visual RAG Flow Diagrams
Run this to see the RAG process visually
"""

def print_option1_flow():
    """Show Option 1: Full Document approach"""
    print("\n" + "="*80)
    print("OPTION 1: FULL DOCUMENT APPROACH")
    print("="*80)
    print("""
    
    ┌─────────────────────────────────────────────────────────────┐
    │                     LARGE DOCUMENT                          │
    │                                                             │
    │  [Page 1] [Page 2] [Page 3] ... [Page 100]                │
    │                                                             │
    │  - Executive Summary                                        │
    │  - Business Overview                                        │
    │  - Risk Factors ◄── User wants info about THIS             │
    │  - Financial Data                                           │
    │  - Future Outlook                                           │
    │  ... 95 more pages ...                                      │
    └─────────────────────────────────────────────────────────────┘
                            │
                            │ Take ALL text
                            ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                      PROMPT TO CLAUDE                       │
    │                                                             │
    │  Question: "What are the risk factors?"                     │
    │                                                             │
    │  Document: [ALL 100 PAGES OF TEXT HERE]                     │
    │                                                             │
    │  Token Count: ~50,000 tokens                                │
    │  Cost: $$$$                                                 │
    │  Time: Slow                                                 │
    └─────────────────────────────────────────────────────────────┘
                            │
                            ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                     CLAUDE'S RESPONSE                       │
    │                                                             │
    │  "Based on the document, the risk factors are..."           │
    │                                                             │
    │  ✅ Accurate (Claude saw everything)                        │
    │  ❌ Expensive (many tokens)                                 │
    │  ❌ Slow (large prompt)                                     │
    │  ❌ May fail if doc too large (context limit)              │
    └─────────────────────────────────────────────────────────────┘

    PROBLEMS:
    • Token limit: Claude has max ~200k tokens
    • Cost: More tokens = more money
    • Speed: Longer to process
    • Effectiveness: Claude less accurate with very long prompts
    """)


def print_option2_flow():
    """Show Option 2: RAG approach"""
    print("\n" + "="*80)
    print("OPTION 2: RAG (RETRIEVAL AUGMENTED GENERATION)")
    print("="*80)
    print("""
    
    STEP 1: PREPROCESSING (Do Once)
    ────────────────────────────────────────────────────────────
    
    ┌─────────────────────────────────────────────────────────────┐
    │                     LARGE DOCUMENT                          │
    │                                                             │
    │  [Page 1] [Page 2] [Page 3] ... [Page 100]                │
    └─────────────────────────────────────────────────────────────┘
                            │
                            │ Split into chunks
                            ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    DOCUMENT CHUNKS                          │
    │                                                             │
    │  Chunk 1: Executive Summary                                 │
    │  Chunk 2: Business Overview                                 │
    │  Chunk 3: Risk Factors ◄── Relevant to question            │
    │  Chunk 4: Strategy                                          │
    │  Chunk 5: Financial Performance                             │
    │  ... Chunk 50 ...                                          │
    └─────────────────────────────────────────────────────────────┘
                            │
                            │ Generate embeddings
                            ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                  VECTOR DATABASE / INDEX                    │
    │                                                             │
    │  Chunk 1: [0.23, 0.45, 0.12, ...] vector                  │
    │  Chunk 2: [0.18, 0.67, 0.34, ...] vector                  │
    │  Chunk 3: [0.91, 0.22, 0.56, ...] vector ◄── Store         │
    │  ...                                                        │
    └─────────────────────────────────────────────────────────────┘
    
    
    STEP 2: QUERY TIME (Do Many Times)
    ────────────────────────────────────────────────────────────
    
    ┌─────────────────────────────────────────────────────────────┐
    │                    USER QUESTION                            │
    │                                                             │
    │  "What are the risk factors?"                               │
    └─────────────────────────────────────────────────────────────┘
                            │
                            │ Convert to vector
                            ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                 SIMILARITY SEARCH                           │
    │                                                             │
    │  Query vector: [0.89, 0.21, 0.54, ...]                    │
    │                                                             │
    │  Compare with all chunk vectors:                            │
    │  • Chunk 1: similarity = 0.45                              │
    │  • Chunk 2: similarity = 0.38                              │
    │  • Chunk 3: similarity = 0.92 ◄── Most relevant!           │
    │  • Chunk 4: similarity = 0.41                              │
    │  • Chunk 5: similarity = 0.29                              │
    └─────────────────────────────────────────────────────────────┘
                            │
                            │ Select top K chunks
                            ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                  RETRIEVED CHUNKS                           │
    │                                                             │
    │  Chunk 3: Risk Factors (0.92 similarity)                    │
    │  Chunk 4: Strategy (0.41 similarity)                        │
    │                                                             │
    │  Only 2-5 chunks instead of all 50!                         │
    └─────────────────────────────────────────────────────────────┘
                            │
                            │ Build focused prompt
                            ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    PROMPT TO CLAUDE                         │
    │                                                             │
    │  Question: "What are the risk factors?"                     │
    │                                                             │
    │  Relevant Sections:                                         │
    │  [Chunk 3: Risk Factors section]                            │
    │  [Chunk 4: Strategy section]                                │
    │                                                             │
    │  Token Count: ~2,000 tokens                                 │
    │  Cost: $                                                    │
    │  Time: Fast                                                 │
    └─────────────────────────────────────────────────────────────┘
                            │
                            ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                   CLAUDE'S RESPONSE                         │
    │                                                             │
    │  "Based on the Risk Factors section..."                     │
    │                                                             │
    │  ✅ Accurate (focused on relevant content)                  │
    │  ✅ Cheap (few tokens)                                      │
    │  ✅ Fast (small prompt)                                     │
    │  ✅ Scales to massive documents                             │
    └─────────────────────────────────────────────────────────────┘

    BENEFITS:
    • No token limit issues
    • 50%+ cost reduction
    • 2x faster
    • Works with 1000+ page documents
    • Can search across multiple documents
    
    TRADE-OFFS:
    • More complex to implement
    • Requires preprocessing step
    • Might miss context if chunks poorly chosen
    • Need to tune parameters (chunk size, top_k, etc.)
    """)


def print_embeddings_explanation():
    """Explain how embeddings work"""
    print("\n" + "="*80)
    print("HOW EMBEDDINGS WORK")
    print("="*80)
    print("""
    
    KEYWORD SEARCH (Simple but Limited)
    ────────────────────────────────────────────────────────────
    
    Question: "What are the company's risks?"
    
    Chunk 1: "The company faces market competition..."
             └─► keyword "company" matches ✓
             
    Chunk 2: "Risk factors include cybersecurity threats..."
             └─► keyword "risk" similar to "risks" ✓
             
    Chunk 3: "Financial performance was strong..."
             └─► no keyword matches ✗
    
    Problem: Misses synonyms and semantic meaning!
    
    
    SEMANTIC SEARCH WITH EMBEDDINGS (Better!)
    ────────────────────────────────────────────────────────────
    
    Text gets converted to vectors (numbers) that capture meaning:
    
    "risk factors" → [0.91, 0.23, 0.87, 0.12, ...]
    "threats"      → [0.89, 0.25, 0.85, 0.14, ...]  ← Similar!
    "revenue"      → [0.12, 0.78, 0.23, 0.91, ...]  ← Different!
    
    Words with similar meanings have similar vectors!
    
    Question: "What are the company's risks?"
              → [0.90, 0.24, 0.86, 0.13, ...]
    
    Compare with chunks:
    Chunk 1: [0.45, 0.67, 0.23, ...]  similarity = 0.38
    Chunk 2: [0.92, 0.21, 0.84, ...]  similarity = 0.95 ◄── Match!
    Chunk 3: [0.15, 0.82, 0.19, ...]  similarity = 0.29
    
    Benefits:
    • Understands "risks" = "threats" = "dangers"
    • Understands context and meaning
    • Works across languages
    • Better retrieval accuracy
    
    
    VECTOR SIMILARITY (Cosine Similarity)
    ────────────────────────────────────────────────────────────
    
    Imagine vectors as arrows in space:
    
              Chunk 2 [risks]
                   ↗
                  ↗  
    Query      ↗ ← Small angle = high similarity!
    [risks]  ↗
            
            
            
                     Chunk 3 [revenue]
                     →
              ← Large angle = low similarity
    
    Cosine similarity = how close the angles are
    • 1.0 = identical
    • 0.5 = somewhat similar  
    • 0.0 = completely different
    """)


def print_chunking_strategies():
    """Show different chunking approaches"""
    print("\n" + "="*80)
    print("CHUNKING STRATEGIES")
    print("="*80)
    print("""
    
    ORIGINAL DOCUMENT:
    ────────────────────────────────────────────────────────────
    
    ## Executive Summary
    We achieved record revenue of $500M this year.
    
    ## Risk Factors
    The company faces several risks: competition, 
    cybersecurity, and regulatory compliance.
    
    ## Financial Performance  
    Revenue: $500M (up 25%)
    Net Income: $75M
    
    
    STRATEGY 1: FIXED-SIZE CHUNKS
    ────────────────────────────────────────────────────────────
    
    Chunk 1: "## Executive Summary\nWe achieved record..."
    Chunk 2: "revenue of $500M this year.\n\n## Risk..."
    Chunk 3: "Factors\nThe company faces several..."
    
    ✅ Simple, works for any text
    ✅ Consistent chunk sizes
    ❌ May split sentences/paragraphs awkwardly
    ❌ Context boundaries ignored
    
    
    STRATEGY 2: SEMANTIC/SECTION CHUNKS
    ────────────────────────────────────────────────────────────
    
    Chunk 1: "## Executive Summary\nWe achieved record 
              revenue of $500M this year."
              
    Chunk 2: "## Risk Factors\nThe company faces several 
              risks: competition, cybersecurity, and 
              regulatory compliance."
              
    Chunk 3: "## Financial Performance\nRevenue: $500M..."
    
    ✅ Respects document structure
    ✅ Keeps related content together
    ✅ Best for structured documents
    ❌ Chunks may be very different sizes
    ❌ Requires parsing document structure
    
    
    STRATEGY 3: SENTENCE CHUNKS
    ────────────────────────────────────────────────────────────
    
    Chunk 1: "We achieved record revenue of $500M this year."
    
    Chunk 2: "The company faces several risks: competition, 
              cybersecurity, and regulatory compliance."
              
    Chunk 3: "Revenue: $500M (up 25%)"
    
    ✅ Natural boundaries
    ✅ Complete thoughts
    ❌ May be too small (lack context)
    ❌ Headers separated from content
    
    
    STRATEGY 4: OVERLAPPING CHUNKS
    ────────────────────────────────────────────────────────────
    
    Chunk 1: "## Executive Summary\nWe achieved..."
                                        ├──────── overlap ────┐
    Chunk 2:                  "We achieved record revenue..."  │
                                                ├─── overlap ──┤
    Chunk 3:                               "revenue of $500M..."
    
    ✅ Prevents splitting related content
    ✅ More context per chunk
    ❌ Redundant information
    ❌ More chunks = more storage/cost
    
    
    RECOMMENDATION:
    • Structured docs (reports, articles) → Semantic chunking
    • General text (emails, notes) → Fixed-size with overlap
    • Very short docs → Sentence chunking
    """)


def print_complete_pipeline():
    """Show complete RAG pipeline with all components"""
    print("\n" + "="*80)
    print("COMPLETE RAG PIPELINE")
    print("="*80)
    print("""
    
    ╔═══════════════════════════════════════════════════════════════╗
    ║                    OFFLINE PREPROCESSING                      ║
    ║                     (Do Once Per Document)                    ║
    ╚═══════════════════════════════════════════════════════════════╝
    
         ┌──────────────────────────────────────────────┐
         │  1. INGEST DOCUMENTS                         │
         │  • Load PDF, DOCX, TXT, HTML, etc.          │
         │  • Extract text content                      │
         │  • Clean and normalize                       │
         └──────────────────────────────────────────────┘
                         │
                         ▼
         ┌──────────────────────────────────────────────┐
         │  2. CHUNK DOCUMENTS                          │
         │  • Choose strategy (semantic, fixed, etc.)   │
         │  • Set chunk_size and overlap                │
         │  • Split into manageable pieces              │
         └──────────────────────────────────────────────┘
                         │
                         ▼
         ┌──────────────────────────────────────────────┐
         │  3. GENERATE EMBEDDINGS                      │
         │  • Use embedding model                       │
         │    (OpenAI, Sentence Transformers, etc.)    │
         │  • Convert text → vector                     │
         └──────────────────────────────────────────────┘
                         │
                         ▼
         ┌──────────────────────────────────────────────┐
         │  4. STORE IN VECTOR DATABASE                 │
         │  • Save chunks + embeddings                  │
         │  • Add metadata (source, date, etc.)         │
         │  • Create indexes for fast search            │
         └──────────────────────────────────────────────┘
    
    
    ╔═══════════════════════════════════════════════════════════════╗
    ║                      ONLINE QUERY FLOW                        ║
    ║                  (Do For Each User Question)                  ║
    ╚═══════════════════════════════════════════════════════════════╝
    
         ┌──────────────────────────────────────────────┐
         │  1. USER ASKS QUESTION                       │
         │  "What are the main risk factors?"           │
         └──────────────────────────────────────────────┘
                         │
                         ▼
         ┌──────────────────────────────────────────────┐
         │  2. QUERY PROCESSING (Optional)              │
         │  • Rephrase question for better search       │
         │  • Extract key entities                      │
         │  • Generate multiple search queries          │
         └──────────────────────────────────────────────┘
                         │
                         ▼
         ┌──────────────────────────────────────────────┐
         │  3. EMBED QUERY                              │
         │  • Convert question to vector                │
         │  • Same model as document embeddings         │
         └──────────────────────────────────────────────┘
                         │
                         ▼
         ┌──────────────────────────────────────────────┐
         │  4. SIMILARITY SEARCH                        │
         │  • Compare query vector to all chunks        │
         │  • Calculate cosine similarity               │
         │  • Rank by relevance score                   │
         └──────────────────────────────────────────────┘
                         │
                         ▼
         ┌──────────────────────────────────────────────┐
         │  5. RETRIEVE TOP-K CHUNKS                    │
         │  • Get most relevant chunks (typically 3-5)  │
         │  • Apply filters (metadata, date, etc.)      │
         │  • Optional: Rerank for better quality       │
         └──────────────────────────────────────────────┘
                         │
                         ▼
         ┌──────────────────────────────────────────────┐
         │  6. BUILD CONTEXT                            │
         │  • Combine retrieved chunks                  │
         │  • Add source citations                      │
         │  • Format for Claude                         │
         └──────────────────────────────────────────────┘
                         │
                         ▼
         ┌──────────────────────────────────────────────┐
         │  7. GENERATE PROMPT                          │
         │  Question: [user question]                   │
         │  Context: [retrieved chunks]                 │
         │  Instructions: Answer based on context       │
         └──────────────────────────────────────────────┘
                         │
                         ▼
         ┌──────────────────────────────────────────────┐
         │  8. CALL CLAUDE API                          │
         │  • Send prompt to Claude                     │
         │  • Receive generated answer                  │
         └──────────────────────────────────────────────┘
                         │
                         ▼
         ┌──────────────────────────────────────────────┐
         │  9. POST-PROCESS RESPONSE                    │
         │  • Add citations to sources                  │
         │  • Format answer                             │
         │  • Log for monitoring                        │
         └──────────────────────────────────────────────┘
                         │
                         ▼
         ┌──────────────────────────────────────────────┐
         │  10. RETURN TO USER                          │
         │  "The main risk factors are: ..."            │
         │  [Sources: Document A, page 15]              │
         └──────────────────────────────────────────────┘
    
    
    PERFORMANCE METRICS TO TRACK:
    • Retrieval accuracy: Are correct chunks retrieved?
    • Answer quality: Is the answer correct and complete?
    • Latency: How long does it take?
    • Cost: How many tokens used?
    • User satisfaction: Thumbs up/down
    """)


if __name__ == "__main__":
    print("\n")
    print("╔" + "═"*78 + "╗")
    print("║" + " "*20 + "RAG VISUAL GUIDE" + " "*42 + "║")
    print("╚" + "═"*78 + "╝")
    
    # Show all diagrams
    print_option1_flow()
    print_option2_flow()
    print_embeddings_explanation()
    print_chunking_strategies()
    print_complete_pipeline()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("""
    RAG is about being smart with context:
    
    1. PREPROCESS once: chunk → embed → store
    2. QUERY many times: search → retrieve → generate
    
    This gives you:
    • Scalability to huge documents
    • Cost reduction (50%+)
    • Speed improvement (2x+)
    • Better focus for Claude
    
    Trade-off: More complexity, but worth it for large documents!
    
    Next: Run the demo files to see it in action!
    • python rag_demo.py          (basic concepts)
    • python rag_advanced.py       (production techniques)
    • python rag_practical.py      (real-world files)
    """)
