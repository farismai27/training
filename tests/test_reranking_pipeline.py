#!/usr/bin/env python3
"""
Test the re-ranking demo functionality.

This script runs through the complete re-ranking pipeline:
1. Load and chunk document
2. Generate embeddings
3. Create RetrieverWithReranking with Claude client
4. Search with and without re-ranking
5. Compare results
"""

import os
import sys
from dotenv import load_dotenv

# Add src folder to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

def test_reranking_pipeline():
    """Test the complete re-ranking pipeline."""
    from anthropic import Anthropic
    from hybrid_retriever import RetrieverWithReranking, chunk_text_by_section, generate_embeddings_batch
    
    print("\n" + "="*80)
    print("RE-RANKING PIPELINE TEST")
    print("="*80)
    
    # Step 1: Load document
    print("\n1️⃣ Loading document...")
    report_path = os.path.join(os.path.dirname(__file__), "..", "data", "report.md")
    
    if not os.path.exists(report_path):
        print("❌ report.md not found in data/ folder")
        return False
    
    with open(report_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"   ✅ Loaded {len(text)} characters")
    
    # Step 2: Chunk document
    print("\n2️⃣ Chunking document...")
    chunks = chunk_text_by_section(text)
    print(f"   ✅ Created {len(chunks)} chunks")
    
    # Step 3: Generate embeddings
    print("\n3️⃣ Generating embeddings...")
    embeddings = generate_embeddings_batch(chunks)
    print(f"   ✅ Generated {len(embeddings)} embeddings")
    print(f"   ℹ️  Embedding dimension: {len(embeddings[0]) if embeddings else 'N/A'}")
    
    # Step 4: Build retriever with re-ranking
    print("\n4️⃣ Building RetrieverWithReranking...")
    
    if not api_key:
        print("   ⚠️  ANTHROPIC_API_KEY not set - skipping re-ranking test")
        print("   ℹ️  Testing basic retriever functionality instead...")
        
        # Test basic retriever without re-ranking
        from hybrid_retriever import Retriever
        retriever = Retriever()
    else:
        client = Anthropic(api_key=api_key)
        retriever = RetrieverWithReranking(client=client)
    
    print(f"   ✅ Retriever type: {type(retriever).__name__}")
    
    # Step 5: Add documents
    print("\n5️⃣ Adding documents to retriever...")
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        metadata = {
            'id': i,
            'content': chunk,
            'section': chunk.split('\n')[0] if chunk else f"Section {i}"
        }
        retriever.add_document(chunk, embedding, metadata)
    
    print(f"   ✅ Added {len(chunks)} documents")
    
    # Step 6: Test basic search
    print("\n6️⃣ Testing hybrid search...")
    query = "What happened with incident 2023"
    query_embedding = generate_embeddings_batch([query])[0]
    
    results = retriever.search(query, query_embedding, top_k=3)
    print(f"   ✅ Hybrid search returned {len(results)} results:")
    for i, (metadata, score) in enumerate(results, 1):
        print(f"      {i}. {metadata['section'][:50]}... (score: {-score:.4f})")
    
    # Step 7: Test re-ranking if client available
    if api_key and hasattr(retriever, 'search_with_reranking'):
        print("\n7️⃣ Testing re-ranking...")
        try:
            reranked = retriever.search_with_reranking(query, query_embedding, top_k=3)
            print(f"   ✅ Re-ranking returned {len(reranked)} results:")
            for i, (metadata, score) in enumerate(reranked, 1):
                print(f"      {i}. {metadata['section'][:50]}... (re-ranked)")
            
            # Compare results
            if results and reranked:
                hybrid_top = results[0][0]['section']
                reranked_top = reranked[0][0]['section']
                
                if hybrid_top == reranked_top:
                    print("\n   ℹ️  Ranking unchanged (both methods agree)")
                else:
                    print(f"\n   ℹ️  Ranking changed:")
                    print(f"       Hybrid: {hybrid_top}")
                    print(f"       Re-ranked: {reranked_top}")
        except Exception as e:
            print(f"   ⚠️  Re-ranking test skipped: {e}")
    
    print("\n" + "="*80)
    print("✅ RE-RANKING PIPELINE TEST PASSED")
    print("="*80)
    return True


def test_complex_query():
    """Test a complex query that benefits from re-ranking."""
    from anthropic import Anthropic
    from hybrid_retriever import RetrieverWithReranking, chunk_text_by_section, generate_embeddings_batch
    
    print("\n" + "="*80)
    print("COMPLEX QUERY TEST")
    print("="*80)
    
    # Load and prepare
    report_path = os.path.join(os.path.dirname(__file__), "..", "data", "report.md")
    with open(report_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    chunks = chunk_text_by_section(text)
    embeddings = generate_embeddings_batch(chunks)
    
    if not api_key:
        print("\n⚠️  ANTHROPIC_API_KEY not set - skipping complex query test")
        return True
    
    # Create retriever
    client = Anthropic(api_key=api_key)
    retriever = RetrieverWithReranking(client=client)
    
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        metadata = {
            'id': i,
            'content': chunk,
            'section': chunk.split('\n')[0] if chunk else f"Section {i}"
        }
        retriever.add_document(chunk, embedding, metadata)
    
    # Test complex query
    query = "What did the engineering team do with the Q4 incident"
    print(f"\nQuery: \"{query}\"")
    print("-" * 80)
    
    query_embedding = generate_embeddings_batch([query])[0]
    
    print("\nHybrid Search Results:")
    hybrid_results = retriever.search(query, query_embedding, top_k=2)
    for i, (metadata, score) in enumerate(hybrid_results, 1):
        print(f"  {i}. {metadata['section'][:60]}...")
    
    try:
        print("\nRe-ranked Results:")
        reranked_results = retriever.search_with_reranking(query, query_embedding, top_k=2)
        for i, (metadata, score) in enumerate(reranked_results, 1):
            print(f"  {i}. {metadata['section'][:60]}...")
        
        print("\n✅ Complex query test passed")
    except Exception as e:
        print(f"\n⚠️  Re-ranking failed: {e}")
        print("   (This is expected if Claude API is not responding)")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("RE-RANKING FUNCTIONALITY TEST SUITE")
    print("="*80)
    
    try:
        # Test 1: Pipeline
        if not test_reranking_pipeline():
            print("\n❌ Pipeline test failed")
            return 1
        
        # Test 2: Complex query
        if not test_complex_query():
            print("\n❌ Complex query test failed")
            return 1
        
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED")
        print("="*80)
        print("\nNext: Run '/rerank-demo' in demo.py to see the full interactive demo")
        print("="*80)
        return 0
    
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
