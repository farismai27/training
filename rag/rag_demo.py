"""
RAG (Retrieval Augmented Generation) Implementation Demo
Based on Anthropic Course - Module on RAG

This demo shows:
1. Option 1: Putting entire document in prompt (simple but limited)
2. Option 2: RAG - Chunking + Retrieval (scalable and efficient)
"""

import os
import re
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise RuntimeError("ANTHROPIC_API_KEY not set. Add it to your .env file.")

client = Anthropic(api_key=api_key)
MODEL = "claude-3-5-haiku-latest"

# =========================
# SAMPLE FINANCIAL DOCUMENT
# =========================
SAMPLE_FINANCIAL_DOCUMENT = """
ACME CORPORATION - ANNUAL REPORT 2025

EXECUTIVE SUMMARY
ACME Corporation is a leading technology company specializing in innovative software solutions. 
This year we achieved record revenue of $500M, representing 25% growth year-over-year.

BUSINESS OVERVIEW
ACME operates in three primary segments: Enterprise Software (60% revenue), Cloud Services (30% revenue), 
and Consulting Services (10% revenue). Our customer base spans 45 countries with over 10,000 active clients.

RISK FACTORS
The company faces several key risks that could impact future performance:

1. MARKET COMPETITION: The software industry is highly competitive with rapid technological change. 
   We face competition from both established players and emerging startups. Failure to innovate 
   could result in loss of market share.

2. CYBERSECURITY THREATS: As a technology company handling sensitive customer data, we are a target 
   for cyber attacks. Any significant data breach could damage our reputation and result in 
   substantial financial losses and legal liabilities.

3. REGULATORY COMPLIANCE: We operate globally and must comply with various data protection regulations 
   including GDPR, CCPA, and emerging AI regulations. Non-compliance could result in significant fines.

4. KEY PERSONNEL DEPENDENCY: Our success depends on retaining key technical and management personnel. 
   Loss of critical employees could disrupt operations and strategic initiatives.

5. ECONOMIC DOWNTURN: A recession could lead customers to reduce IT spending, negatively impacting 
   our revenue and profitability.

STRATEGY OUTLOOK
Our strategy focuses on three pillars:
- Expanding our AI/ML capabilities to address emerging customer needs
- Growing our cloud infrastructure to support enterprise scalability
- Strategic acquisitions to enter adjacent markets

We are investing $50M in R&D this year, particularly in generative AI technologies. This positions us 
to address the cybersecurity risks mentioned earlier through advanced threat detection systems.

FINANCIAL PERFORMANCE
Revenue: $500M (up 25% YoY)
Operating Income: $100M (20% margin)
Net Income: $75M
Cash and Equivalents: $200M
Total Assets: $800M
Total Liabilities: $300M
Stockholders' Equity: $500M

The strong balance sheet provides cushion against economic downturns and allows us to pursue 
strategic growth opportunities.

FUTURE OUTLOOK
We expect continued growth driven by digital transformation trends. However, we acknowledge the 
competitive landscape and regulatory uncertainties as key challenges. Our diversified revenue 
streams and strong financial position provide resilience against market volatility.
"""


# =========================
# OPTION 1: ENTIRE DOCUMENT IN PROMPT
# =========================
def option1_full_document(document: str, question: str) -> str:
    """
    Option 1: Put the entire document in the prompt.
    
    PROS:
    - Simple implementation
    - Claude sees all context
    
    CONS:
    - May exceed token limits for large documents
    - Less effective with very long prompts
    - More expensive and slower
    - Doesn't scale to multiple documents
    """
    prompt = f"""You are a financial analyst assistant. Answer the user's question based on the document provided.

Document:
{document}

User Question: {question}

Please provide a clear, concise answer based only on information in the document."""

    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text


# =========================
# OPTION 2: RAG IMPLEMENTATION
# =========================

def chunk_document_by_sections(document: str) -> List[Dict[str, str]]:
    """
    Step 1 of RAG: Break document into chunks.
    
    This implementation chunks by sections (headers in uppercase).
    Other strategies could include:
    - Fixed-size chunks (e.g., every 500 characters)
    - Sentence-based chunks
    - Paragraph-based chunks
    - Semantic chunks (more advanced)
    """
    chunks = []
    
    # Split by section headers (lines in all caps)
    lines = document.strip().split('\n')
    current_chunk = []
    current_header = "Introduction"
    
    for line in lines:
        # Check if line is a header (all caps, not empty)
        if line.strip() and line.strip().isupper() and len(line.strip()) > 3:
            # Save previous chunk if it exists
            if current_chunk:
                chunks.append({
                    "header": current_header,
                    "content": '\n'.join(current_chunk).strip()
                })
            # Start new chunk
            current_header = line.strip()
            current_chunk = [line]
        else:
            current_chunk.append(line)
    
    # Add the last chunk
    if current_chunk:
        chunks.append({
            "header": current_header,
            "content": '\n'.join(current_chunk).strip()
        })
    
    return chunks


def simple_relevance_search(question: str, chunks: List[Dict[str, str]], top_k: int = 2) -> List[Dict[str, str]]:
    """
    Step 2 of RAG: Find relevant chunks based on the question.
    
    This is a SIMPLE keyword-based approach for demonstration.
    Production systems would use:
    - Embedding models (semantic similarity)
    - Vector databases (Pinecone, Weaviate, etc.)
    - More sophisticated ranking algorithms
    """
    # Extract keywords from question (simple approach)
    question_lower = question.lower()
    question_words = set(re.findall(r'\b\w+\b', question_lower))
    
    # Score each chunk by keyword overlap
    scored_chunks = []
    for chunk in chunks:
        chunk_lower = (chunk['header'] + ' ' + chunk['content']).lower()
        chunk_words = set(re.findall(r'\b\w+\b', chunk_lower))
        
        # Calculate simple overlap score
        overlap = len(question_words & chunk_words)
        
        # Bonus for header matches
        header_matches = sum(1 for word in question_words if word in chunk['header'].lower())
        score = overlap + (header_matches * 3)
        
        scored_chunks.append((score, chunk))
    
    # Sort by score and return top_k
    scored_chunks.sort(reverse=True, key=lambda x: x[0])
    return [chunk for score, chunk in scored_chunks[:top_k]]


def option2_rag(document: str, question: str, top_k: int = 2) -> Tuple[str, List[Dict[str, str]]]:
    """
    Option 2: RAG - Retrieval Augmented Generation
    
    PROS:
    - Scales to very large documents (100-1000+ pages)
    - Works with multiple documents
    - Smaller prompts = faster and cheaper
    - Claude focuses on relevant content
    
    CONS:
    - More complex implementation
    - Requires preprocessing step
    - Need to define chunking strategy
    - Need search/retrieval mechanism
    - May miss context if wrong chunks selected
    """
    # Step 1: Chunk the document (preprocessing - do this once)
    chunks = chunk_document_by_sections(document)
    
    print(f"\n📄 Document chunked into {len(chunks)} sections")
    print(f"📋 Sections: {[c['header'] for c in chunks]}")
    
    # Step 2: Retrieve relevant chunks based on question
    relevant_chunks = simple_relevance_search(question, chunks, top_k=top_k)
    
    print(f"\n🔍 Retrieved {len(relevant_chunks)} most relevant sections:")
    for chunk in relevant_chunks:
        print(f"   - {chunk['header']}")
    
    # Step 3: Build prompt with only relevant chunks
    chunks_text = "\n\n".join([
        f"Section: {chunk['header']}\n{chunk['content']}" 
        for chunk in relevant_chunks
    ])
    
    prompt = f"""You are a financial analyst assistant. Answer the user's question based on the relevant document sections provided.

Relevant Document Sections:
{chunks_text}

User Question: {question}

Please provide a clear, concise answer based only on information in the provided sections."""

    # Step 4: Get response from Claude
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text, relevant_chunks


# =========================
# COMPARISON DEMO
# =========================
def compare_approaches(question: str):
    """
    Compare both approaches side-by-side
    """
    print("=" * 80)
    print(f"Question: {question}")
    print("=" * 80)
    
    # Option 1
    print("\n🔷 OPTION 1: Full Document Approach")
    print("-" * 80)
    answer1 = option1_full_document(SAMPLE_FINANCIAL_DOCUMENT, question)
    print(f"Answer: {answer1}")
    print(f"\nPrompt size: ~{len(SAMPLE_FINANCIAL_DOCUMENT) + len(question)} characters")
    
    # Option 2
    print("\n\n🔶 OPTION 2: RAG Approach")
    print("-" * 80)
    answer2, retrieved_chunks = option2_rag(SAMPLE_FINANCIAL_DOCUMENT, question, top_k=2)
    print(f"\nAnswer: {answer2}")
    
    chunks_size = sum(len(c['content']) for c in retrieved_chunks)
    print(f"\nPrompt size: ~{chunks_size + len(question)} characters")
    print(f"Reduction: {100 * (1 - chunks_size / len(SAMPLE_FINANCIAL_DOCUMENT)):.1f}%")


# =========================
# ADVANCED: VECTOR-BASED RETRIEVAL (CONCEPT)
# =========================
def advanced_rag_concept():
    """
    In production RAG systems, you would typically use:
    
    1. EMBEDDING MODELS to convert text to vectors:
       - OpenAI embeddings (text-embedding-ada-002)
       - Sentence transformers (all-MiniLM-L6-v2)
       - Anthropic embeddings (when available)
    
    2. VECTOR DATABASES for efficient similarity search:
       - Pinecone
       - Weaviate
       - Chroma
       - FAISS
       - Qdrant
    
    3. ADVANCED CHUNKING STRATEGIES:
       - Recursive character splitting
       - Semantic chunking
       - Overlapping chunks
       - Parent-child documents
    
    4. RERANKING:
       - After initial retrieval, rerank chunks for better relevance
       - Use cross-encoder models
    
    5. HYBRID SEARCH:
       - Combine keyword search + vector search
       - BM25 + semantic similarity
    
    Example workflow:
    ```python
    # Preprocessing (once)
    chunks = chunk_document(document)
    embeddings = [embed(chunk) for chunk in chunks]
    vector_db.store(chunks, embeddings)
    
    # At query time
    query_embedding = embed(question)
    relevant_chunks = vector_db.similarity_search(query_embedding, top_k=3)
    relevant_chunks = rerank(question, relevant_chunks)
    answer = claude.generate(question, relevant_chunks)
    ```
    """
    pass


# =========================
# MAIN EXECUTION
# =========================
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RAG (RETRIEVAL AUGMENTED GENERATION) DEMO")
    print("Based on Anthropic Course")
    print("=" * 80)
    
    # Sample questions
    questions = [
        "What risk factors does this company have?",
        "What is the company's revenue?",
        "How is the company addressing cybersecurity risks?",
    ]
    
    # Run comparison for each question
    for question in questions:
        compare_approaches(question)
        print("\n\n")
    
    # Show key concepts
    print("\n" + "=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print("""
1. RAG is essential for working with large documents (100-1000+ pages)
2. RAG reduces prompt size, cost, and latency
3. RAG allows Claude to focus on relevant content
4. Main challenges:
   - Choosing chunking strategy
   - Implementing effective retrieval
   - Ensuring retrieved chunks have sufficient context
5. Production RAG uses embeddings + vector databases (not keyword search)
6. Consider Option 1 (full document) for small documents (<10k tokens)
7. Consider Option 2 (RAG) for large documents or multiple documents
    """)
