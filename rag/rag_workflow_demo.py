"""
RAG Workflow Demo - Complete 5-Step Process
Based on Anthropic Course: 003 VectorDB Lesson

This implements the complete RAG pipeline:
1. Chunk the document
2. Generate embeddings for each chunk
3. Store embeddings in vector index
4. Generate embedding for user query
5. Search for relevant chunks

Run with: python rag_workflow_demo.py
"""

import os
import re


class SimpleVectorIndex:
    """Simple in-memory vector index for RAG demonstration.
    
    This implements the core concepts from the Anthropic course:
    - Store embeddings with associated content
    - Search using cosine similarity  
    - Return most relevant chunks
    """
    
    def __init__(self):
        self.vectors = []
        self.metadata = []
    
    def add_vector(self, embedding, metadata):
        """Add a vector and its associated metadata to the index."""
        self.vectors.append(embedding)
        self.metadata.append(metadata)
    
    def search(self, query_embedding, top_k=2):
        """Search for most similar vectors using cosine similarity.
        
        Returns list of (metadata, cosine_distance) tuples.
        Cosine distance = 1 - cosine_similarity (closer to 0 = more similar)
        """
        if not self.vectors:
            return []
        
        results = []
        
        # Calculate cosine similarity for each stored vector
        for i, stored_embedding in enumerate(self.vectors):
            # Cosine similarity = dot product / (magnitude1 * magnitude2)
            dot_product = sum(a * b for a, b in zip(query_embedding, stored_embedding))
            
            magnitude_query = sum(x * x for x in query_embedding) ** 0.5
            magnitude_stored = sum(x * x for x in stored_embedding) ** 0.5
            
            cosine_similarity = dot_product / (magnitude_query * magnitude_stored)
            
            # Convert to cosine distance (1 - similarity)
            # Distance closer to 0 means more similar
            cosine_distance = 1 - cosine_similarity
            
            results.append((self.metadata[i], cosine_distance))
        
        # Sort by distance (ascending - closest first)
        results.sort(key=lambda x: x[1])
        
        # Return top_k results
        return results[:top_k]


def chunk_text_by_section(text):
    """Chunk text by markdown sections (structure-based chunking)."""
    # Split on markdown headers (## Section)
    pattern = r'\n(?=## )'
    chunks = re.split(pattern, text)
    
    # Clean up chunks
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    
    return chunks


def generate_embeddings_batch(texts):
    """Generate embeddings for multiple texts.
    
    This tries to use sentence-transformers for real embeddings,
    or falls back to simulated embeddings for demonstration.
    """
    try:
        # Try to use sentence-transformers if available
        from sentence_transformers import SentenceTransformer
        print("[INFO] Using sentence-transformers for embeddings")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(texts, show_progress_bar=False)
        return [embedding.tolist() for embedding in embeddings]
    except ImportError:
        # Fallback: Create simple simulated embeddings based on text characteristics
        print("[INFO] Using simulated embeddings (install sentence-transformers for real embeddings)")
        print("       Run: pip install sentence-transformers")
        embeddings = []
        for text in texts:
            # Create a simple embedding based on text features
            # This is NOT production-quality, just for demonstration
            text_lower = text.lower()
            
            # Feature 1: Medical/health keywords
            medical_score = sum([
                text_lower.count('medical'),
                text_lower.count('health'),
                text_lower.count('patient'),
                text_lower.count('research'),
                text_lower.count('drug'),
                text_lower.count('treatment'),
                text_lower.count('clinical'),
                text_lower.count('disease')
            ]) / max(len(text), 1) * 1000
            
            # Feature 2: Software/engineering keywords  
            software_score = sum([
                text_lower.count('software'),
                text_lower.count('engineer'),
                text_lower.count('bug'),
                text_lower.count('code'),
                text_lower.count('develop'),
                text_lower.count('program'),
                text_lower.count('system'),
                text_lower.count('platform')
            ]) / max(len(text), 1) * 1000
            
            # Feature 3: Business keywords
            business_score = sum([
                text_lower.count('revenue'),
                text_lower.count('profit'),
                text_lower.count('business'),
                text_lower.count('company'),
                text_lower.count('market'),
                text_lower.count('customer'),
                text_lower.count('financial'),
                text_lower.count('income')
            ]) / max(len(text), 1) * 1000
            
            # Normalize to create simple 3D embedding
            total = medical_score + software_score + business_score + 0.001
            embedding = [
                medical_score / total,
                software_score / total,
                business_score / total
            ]
            
            embeddings.append(embedding)
        
        return embeddings


def main():
    """Run the complete RAG workflow demonstration."""
    print("\n" + "="*80)
    print("RAG WORKFLOW DEMO - Complete 5-Step Process")
    print("Based on Anthropic Course: 003 VectorDB Lesson")
    print("="*80 + "\n")
    
    # Check if report file exists
    report_path = "report.md"
    if not os.path.exists(report_path):
        print("❌ report.md not found in current directory")
        print("\nPlease ensure report.md exists in the same directory as this script.")
        return
    
    # STEP 1: Read and chunk the document
    print("📄 STEP 1: Chunking the document by sections")
    print("-" * 80)
    
    with open(report_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    chunks = chunk_text_by_section(text)
    
    print(f"✅ Created {len(chunks)} chunks\n")
    
    # Show first few chunks (preview)
    for i, chunk in enumerate(chunks[:3], 1):
        preview = chunk[:150].replace('\n', ' ')
        print(f"  Chunk {i}: {preview}...")
    
    if len(chunks) > 3:
        print(f"  ... and {len(chunks) - 3} more chunks")
    
    print()
    
    # STEP 2: Generate embeddings for each chunk
    print("🔢 STEP 2: Generating embeddings for each chunk")
    print("-" * 80)
    
    embeddings = generate_embeddings_batch(chunks)
    
    print(f"✅ Generated {len(embeddings)} embeddings")
    print(f"   Embedding dimensions: {len(embeddings[0])}")
    print(f"   Example embedding (first 5 values): {[f'{x:.4f}' for x in embeddings[0][:5]]}")
    print()
    
    # STEP 3: Create vector index and store embeddings
    print("💾 STEP 3: Storing embeddings in vector index")
    print("-" * 80)
    
    store = SimpleVectorIndex()
    
    for embedding, chunk in zip(embeddings, chunks):
        store.add_vector(embedding, {"content": chunk})
    
    print(f"✅ Stored {len(chunks)} vectors in index")
    print()
    
    # STEP 4: User asks a question, generate embedding
    print("❓ STEP 4: Processing user query")
    print("-" * 80)
    
    user_question = "What did the software engineering department do last year?"
    print(f'User question: "{user_question}"')
    print()
    
    user_embedding = generate_embeddings_batch([user_question])[0]
    
    print(f"✅ Generated query embedding")
    print(f"   Query embedding (first 5 values): {[f'{x:.4f}' for x in user_embedding[:5]]}")
    print()
    
    # STEP 5: Search for relevant chunks
    print("🔍 STEP 5: Searching for relevant chunks")
    print("-" * 80)
    
    results = store.search(user_embedding, top_k=2)
    
    print(f"✅ Found top {len(results)} most relevant chunks:\n")
    
    for i, (doc, distance) in enumerate(results, 1):
        # Cosine similarity = 1 - distance
        similarity = 1 - distance
        
        print(f"Result #{i}:")
        print(f"  Cosine Distance: {distance:.4f}")
        print(f"  Cosine Similarity: {similarity:.4f}")
        
        # Show section header if present
        content = doc['content']
        lines = content.split('\n')
        header = lines[0] if lines else "No header"
        print(f"  Section: {header}")
        
        # Show preview
        preview = content[:300].replace('\n', ' ')
        print(f"  Content: {preview}...")
        print()
    
    # Show what would happen next in RAG
    print("="*80)
    print("NEXT STEPS IN FULL RAG PIPELINE:")
    print("="*80)
    print("✅ Take these relevant chunks")
    print("✅ Add them as context to the prompt")
    print("✅ Send to Claude with user question")
    print("✅ Claude generates answer based on relevant context")
    print()
    print("Example prompt structure:")
    print("-" * 80)
    
    context = "\n\n".join([doc['content'][:400] for doc, _ in results])
    
    example_prompt = f"""You are a helpful assistant. Answer the user's question based on the provided context.

Context:
{context}

User Question: {user_question}

Answer based only on the context provided above."""
    
    print(example_prompt)
    print()
    
    # Explain the math
    print("="*80)
    print("UNDERSTANDING THE MATH:")
    print("="*80)
    print("""
Cosine Similarity measures the angle between two vectors:
  • Value of 1.0 = vectors point in same direction (very similar)
  • Value of 0.0 = vectors are perpendicular (not similar)
  • Value of -1.0 = vectors point in opposite directions

Cosine Distance = 1 - Cosine Similarity:
  • Distance of 0.0 = perfect match
  • Distance of 1.0 = completely different
  • Smaller distance = more similar chunks

Formula: 
  cosine_similarity = dot_product / (magnitude1 × magnitude2)
  where:
    dot_product = sum(a[i] * b[i] for all i)
    magnitude = sqrt(sum(x[i]² for all i))

This is exactly what vector databases do at scale!
    """)
    
    print("="*80)
    print("TRY IT YOURSELF:")
    print("="*80)
    print("\n1. Modify the user_question variable to ask different questions")
    print("2. Try changing top_k to retrieve more/fewer chunks")
    print("3. Experiment with different chunking strategies")
    print("4. Install sentence-transformers for real embeddings:")
    print("   pip install sentence-transformers")
    print()


if __name__ == "__main__":
    main()
