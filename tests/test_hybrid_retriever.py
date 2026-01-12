#!/usr/bin/env python3
"""
Quick test script for the hybrid retriever implementation.
Run this to verify everything is working correctly.
"""

import os
import sys

def test_hybrid_retriever():
    """Test the hybrid retriever implementation."""
    
    print("\n" + "="*80)
    print("HYBRID RETRIEVER - QUICK TEST")
    print("="*80 + "\n")
    
    # Test 1: Import the module
    print("Test 1: Importing hybrid_retriever module...")
    try:
        from hybrid_retriever import (
            Retriever, 
            SimpleVectorIndex, 
            BM25Index, 
            chunk_text_by_section, 
            generate_embeddings_batch
        )
        print("✅ Successfully imported all components\n")
    except ImportError as e:
        print(f"❌ Import failed: {e}\n")
        return False
    
    # Test 2: Check for report.md
    print("Test 2: Checking for report.md...")
    if not os.path.exists("report.md"):
        print("❌ report.md not found")
        print("   Create it with sample content first\n")
        return False
    print("✅ report.md found\n")
    
    # Test 3: Load and chunk document
    print("Test 3: Loading and chunking document...")
    try:
        with open("report.md", 'r', encoding='utf-8') as f:
            text = f.read()
        
        chunks = chunk_text_by_section(text)
        print(f"✅ Created {len(chunks)} chunks\n")
    except Exception as e:
        print(f"❌ Failed: {e}\n")
        return False
    
    # Test 4: Generate embeddings
    print("Test 4: Generating embeddings...")
    try:
        embeddings = generate_embeddings_batch(chunks)
        print(f"✅ Generated {len(embeddings)} embeddings")
        print(f"   Dimension: {len(embeddings[0]) if embeddings else 0}\n")
    except Exception as e:
        print(f"❌ Failed: {e}\n")
        return False
    
    # Test 5: Build retriever
    print("Test 5: Building hybrid retriever...")
    try:
        retriever = Retriever()
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            metadata = {
                'id': i,
                'content': chunk,
                'section': chunk.split('\n')[0] if chunk else f"Section {i}"
            }
            retriever.add_document(chunk, embedding, metadata)
        
        print(f"✅ Built retriever with {len(chunks)} documents\n")
    except Exception as e:
        print(f"❌ Failed: {e}\n")
        return False
    
    # Test 6: Test semantic search
    print("Test 6: Testing semantic search...")
    try:
        query = "incident 2023"
        query_embedding = generate_embeddings_batch([query])[0]
        
        results = retriever.vector_index.search(query_embedding, top_k=2)
        print(f"✅ Semantic search returned {len(results)} results")
        for i, (metadata, distance) in enumerate(results, 1):
            print(f"   {i}. {metadata['section']} (distance: {distance:.4f})\n")
    except Exception as e:
        print(f"❌ Failed: {e}\n")
        return False
    
    # Test 7: Test lexical search
    print("Test 7: Testing lexical search (BM25)...")
    try:
        results = retriever.bm25_index.search(query, top_k=2)
        print(f"✅ BM25 search returned {len(results)} results")
        for i, (metadata, score) in enumerate(results, 1):
            print(f"   {i}. {metadata['section']} (score: {-score:.4f})\n")
    except Exception as e:
        print(f"❌ Failed: {e}\n")
        return False
    
    # Test 8: Test hybrid search
    print("Test 8: Testing hybrid search (RRF)...")
    try:
        results = retriever.search(query, query_embedding, top_k=2)
        print(f"✅ Hybrid search returned {len(results)} results")
        for i, (metadata, rrf_score) in enumerate(results, 1):
            print(f"   {i}. {metadata['section']} (RRF score: {-rrf_score:.4f})\n")
    except Exception as e:
        print(f"❌ Failed: {e}\n")
        return False
    
    print("="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80)
    print("\nYou can now:")
    print("  1. Run 'python demo.py' and type '/hybrid-demo'")
    print("  2. Open '005_hybrid_retrieval.ipynb' in Jupyter")
    print("  3. Use hybrid_retriever.py in your own code")
    print()
    
    return True


if __name__ == "__main__":
    success = test_hybrid_retriever()
    sys.exit(0 if success else 1)
