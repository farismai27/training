"""
Advanced RAG Implementation with Vector Embeddings
Using sentence-transformers for semantic similarity

Install required package:
pip install sentence-transformers numpy

This demonstrates production-grade RAG with:
- Semantic embeddings (not just keyword matching)
- Cosine similarity for retrieval
- Multiple chunking strategies
- Evaluation of different approaches
"""

import os
import re
import numpy as np
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv
from anthropic import Anthropic

# Optional: Only import if user has sentence-transformers installed
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("⚠️  sentence-transformers not installed. Install with: pip install sentence-transformers")

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise RuntimeError("ANTHROPIC_API_KEY not set.")

client = Anthropic(api_key=api_key)
MODEL = "claude-3-5-haiku-latest"


# =========================
# CHUNKING STRATEGIES
# =========================

class ChunkingStrategy:
    """Base class for different chunking strategies"""
    
    @staticmethod
    def chunk(text: str, **kwargs) -> List[Dict[str, str]]:
        raise NotImplementedError


class FixedSizeChunking(ChunkingStrategy):
    """Split text into fixed-size chunks with optional overlap"""
    
    @staticmethod
    def chunk(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, str]]:
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            
            chunks.append({
                "content": chunk_text.strip(),
                "start": start,
                "end": min(end, len(text)),
                "strategy": "fixed_size"
            })
            
            start = end - overlap
        
        return chunks


class SentenceChunking(ChunkingStrategy):
    """Split text into chunks by sentences, grouping N sentences together"""
    
    @staticmethod
    def chunk(text: str, sentences_per_chunk: int = 3) -> List[Dict[str, str]]:
        # Simple sentence splitting (production would use nltk or spacy)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        
        for i in range(0, len(sentences), sentences_per_chunk):
            chunk_sentences = sentences[i:i + sentences_per_chunk]
            chunk_text = ' '.join(chunk_sentences)
            
            chunks.append({
                "content": chunk_text.strip(),
                "sentence_range": f"{i}-{i + len(chunk_sentences)}",
                "strategy": "sentence"
            })
        
        return chunks


class ParagraphChunking(ChunkingStrategy):
    """Split text by paragraphs"""
    
    @staticmethod
    def chunk(text: str) -> List[Dict[str, str]]:
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = []
        
        for idx, para in enumerate(paragraphs):
            chunks.append({
                "content": para,
                "paragraph_num": idx,
                "strategy": "paragraph"
            })
        
        return chunks


class SemanticSectionChunking(ChunkingStrategy):
    """Split by semantic sections (headers, topics)"""
    
    @staticmethod
    def chunk(text: str) -> List[Dict[str, str]]:
        chunks = []
        lines = text.strip().split('\n')
        current_chunk = []
        current_header = "Introduction"
        
        for line in lines:
            # Detect headers (all caps or starts with ##)
            if (line.strip() and line.strip().isupper() and len(line.strip()) > 3) or \
               line.strip().startswith('##'):
                if current_chunk:
                    chunks.append({
                        "content": '\n'.join(current_chunk).strip(),
                        "header": current_header,
                        "strategy": "semantic"
                    })
                current_header = line.strip()
                current_chunk = [line]
            else:
                current_chunk.append(line)
        
        if current_chunk:
            chunks.append({
                "content": '\n'.join(current_chunk).strip(),
                "header": current_header,
                "strategy": "semantic"
            })
        
        return chunks


# =========================
# RETRIEVAL MECHANISMS
# =========================

class VectorRetriever:
    """Semantic retrieval using embeddings and cosine similarity"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        if not EMBEDDINGS_AVAILABLE:
            raise RuntimeError("sentence-transformers required for VectorRetriever")
        
        self.model = SentenceTransformer(model_name)
        self.chunks: List[Dict] = []
        self.embeddings: Optional[np.ndarray] = None
    
    def index_chunks(self, chunks: List[Dict[str, str]]):
        """Preprocess: Generate embeddings for all chunks"""
        self.chunks = chunks
        texts = [chunk['content'] for chunk in chunks]
        
        print(f"🔄 Generating embeddings for {len(chunks)} chunks...")
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        print(f"✅ Embeddings generated: shape {self.embeddings.shape}")
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """Retrieve top_k most relevant chunks based on semantic similarity"""
        if self.embeddings is None:
            raise RuntimeError("Must call index_chunks() before retrieve()")
        
        # Encode query
        query_embedding = self.model.encode([query])[0]
        
        # Calculate cosine similarity
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top_k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Return chunks with scores
        results = [(self.chunks[idx], similarities[idx]) for idx in top_indices]
        return results


class KeywordRetriever:
    """Simple keyword-based retrieval (BM25-like)"""
    
    def __init__(self):
        self.chunks: List[Dict] = []
    
    def index_chunks(self, chunks: List[Dict[str, str]]):
        self.chunks = chunks
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """Retrieve based on keyword overlap"""
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        
        scored_chunks = []
        for chunk in self.chunks:
            content_words = set(re.findall(r'\b\w+\b', chunk['content'].lower()))
            
            # Calculate overlap score
            overlap = len(query_words & content_words)
            total_words = len(content_words)
            score = overlap / max(total_words, 1)
            
            scored_chunks.append((chunk, score))
        
        # Sort by score
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return scored_chunks[:top_k]


class HybridRetriever:
    """Combine keyword and semantic retrieval"""
    
    def __init__(self, alpha: float = 0.5):
        """
        alpha: weight for semantic score
        (1-alpha): weight for keyword score
        """
        if not EMBEDDINGS_AVAILABLE:
            raise RuntimeError("sentence-transformers required for HybridRetriever")
        
        self.alpha = alpha
        self.vector_retriever = VectorRetriever()
        self.keyword_retriever = KeywordRetriever()
    
    def index_chunks(self, chunks: List[Dict[str, str]]):
        self.vector_retriever.index_chunks(chunks)
        self.keyword_retriever.index_chunks(chunks)
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """Combine scores from both retrievers"""
        # Get results from both
        vector_results = self.vector_retriever.retrieve(query, top_k=len(self.vector_retriever.chunks))
        keyword_results = self.keyword_retriever.retrieve(query, top_k=len(self.keyword_retriever.chunks))
        
        # Normalize and combine scores
        vector_scores = {id(r[0]): r[1] for r in vector_results}
        keyword_scores = {id(r[0]): r[1] for r in keyword_results}
        
        # Calculate hybrid scores
        hybrid_scores = []
        for chunk in self.vector_retriever.chunks:
            chunk_id = id(chunk)
            vec_score = vector_scores.get(chunk_id, 0)
            kw_score = keyword_scores.get(chunk_id, 0)
            
            hybrid_score = self.alpha * vec_score + (1 - self.alpha) * kw_score
            hybrid_scores.append((chunk, hybrid_score))
        
        # Sort and return top_k
        hybrid_scores.sort(key=lambda x: x[1], reverse=True)
        return hybrid_scores[:top_k]


# =========================
# RAG PIPELINE
# =========================

class RAGPipeline:
    """Complete RAG pipeline with configurable components"""
    
    def __init__(self, chunking_strategy: ChunkingStrategy, retriever):
        self.chunking_strategy = chunking_strategy
        self.retriever = retriever
        self.document_indexed = False
    
    def index_document(self, document: str, **chunk_kwargs):
        """Preprocessing: chunk and index document"""
        print(f"\n📄 Chunking document with {self.chunking_strategy.__name__}...")
        chunks = self.chunking_strategy.chunk(document, **chunk_kwargs)
        print(f"✅ Created {len(chunks)} chunks")
        
        print(f"\n🔍 Indexing chunks with {self.retriever.__class__.__name__}...")
        self.retriever.index_chunks(chunks)
        self.document_indexed = True
        
        return chunks
    
    def query(self, question: str, top_k: int = 3) -> Tuple[str, List[Tuple[Dict, float]]]:
        """Query the document and generate answer"""
        if not self.document_indexed:
            raise RuntimeError("Must index document first")
        
        # Retrieve relevant chunks
        print(f"\n🔎 Retrieving top {top_k} chunks for question...")
        results = self.retriever.retrieve(question, top_k=top_k)
        
        print(f"📋 Retrieved chunks (with relevance scores):")
        for chunk, score in results:
            preview = chunk['content'][:100].replace('\n', ' ')
            print(f"   - Score {score:.3f}: {preview}...")
        
        # Build prompt
        chunks_text = "\n\n".join([
            f"[Relevance: {score:.2f}]\n{chunk['content']}"
            for chunk, score in results
        ])
        
        prompt = f"""You are an expert analyst. Answer the question based on the provided document excerpts.

Document Excerpts:
{chunks_text}

Question: {question}

Provide a clear, accurate answer based only on the information given."""
        
        # Get answer from Claude
        message = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text, results


# =========================
# SAMPLE USAGE & COMPARISON
# =========================

SAMPLE_DOC = """
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
"""


def demo_basic_rag():
    """Simple RAG demo - good starting point"""
    print("\n" + "="*80)
    print("BASIC RAG DEMO")
    print("="*80)
    
    if not EMBEDDINGS_AVAILABLE:
        print("⚠️  Skipping: sentence-transformers not installed")
        return
    
    # Create RAG pipeline with semantic chunking + vector retrieval
    pipeline = RAGPipeline(
        chunking_strategy=SemanticSectionChunking,
        retriever=VectorRetriever()
    )
    
    # Index document
    pipeline.index_document(SAMPLE_DOC)
    
    # Query
    question = "What are the main risk factors for this company?"
    answer, retrieved_chunks = pipeline.query(question, top_k=2)
    
    print(f"\n❓ Question: {question}")
    print(f"\n💡 Answer:\n{answer}")


def compare_chunking_strategies():
    """Compare different chunking approaches"""
    print("\n" + "="*80)
    print("CHUNKING STRATEGY COMPARISON")
    print("="*80)
    
    if not EMBEDDINGS_AVAILABLE:
        print("⚠️  Skipping: sentence-transformers not installed")
        return
    
    strategies = [
        (SemanticSectionChunking, {}),
        (FixedSizeChunking, {"chunk_size": 300, "overlap": 50}),
        (SentenceChunking, {"sentences_per_chunk": 2}),
    ]
    
    question = "What are the cybersecurity risks?"
    
    for strategy_class, kwargs in strategies:
        print(f"\n{'='*80}")
        print(f"Strategy: {strategy_class.__name__}")
        print('='*80)
        
        pipeline = RAGPipeline(strategy_class, VectorRetriever())
        pipeline.index_document(SAMPLE_DOC, **kwargs)
        answer, _ = pipeline.query(question, top_k=2)
        
        print(f"\nAnswer: {answer}")


def compare_retrieval_methods():
    """Compare keyword vs semantic vs hybrid retrieval"""
    print("\n" + "="*80)
    print("RETRIEVAL METHOD COMPARISON")
    print("="*80)
    
    if not EMBEDDINGS_AVAILABLE:
        print("⚠️  Skipping: sentence-transformers not installed")
        return
    
    retrievers = [
        ("Keyword", KeywordRetriever()),
        ("Semantic (Vector)", VectorRetriever()),
        ("Hybrid", HybridRetriever(alpha=0.7)),
    ]
    
    question = "How is the company investing in AI?"
    
    for name, retriever in retrievers:
        print(f"\n{'='*80}")
        print(f"Retriever: {name}")
        print('='*80)
        
        pipeline = RAGPipeline(SemanticSectionChunking, retriever)
        pipeline.index_document(SAMPLE_DOC)
        answer, _ = pipeline.query(question, top_k=2)
        
        print(f"\nAnswer: {answer}")


if __name__ == "__main__":
    if not EMBEDDINGS_AVAILABLE:
        print("\n" + "="*80)
        print("SETUP REQUIRED")
        print("="*80)
        print("\nTo run advanced RAG examples, install:")
        print("  pip install sentence-transformers numpy")
        print("\nThis will enable semantic search with embeddings.")
        print("="*80)
    else:
        # Run demos
        demo_basic_rag()
        
        print("\n\n")
        compare_chunking_strategies()
        
        print("\n\n")
        compare_retrieval_methods()
    
    print("\n" + "="*80)
    print("KEY CONCEPTS")
    print("="*80)
    print("""
1. CHUNKING STRATEGIES affect what context is retrieved
   - Semantic: Best for well-structured documents
   - Fixed-size: Simple, works for any text
   - Sentence/Paragraph: Natural boundaries
   
2. RETRIEVAL METHODS determine relevance matching
   - Keyword: Fast, simple, misses synonyms
   - Semantic: Understands meaning, slower, needs embeddings
   - Hybrid: Best of both worlds
   
3. PRODUCTION RAG typically uses:
   - Embeddings (sentence-transformers, OpenAI, etc.)
   - Vector databases (Pinecone, Weaviate, Chroma)
   - Reranking for better results
   - Metadata filtering
   
4. TUNING PARAMETERS:
   - chunk_size: Balance between context and precision
   - top_k: More chunks = more context but longer prompts
   - overlap: Prevents splitting related content
   - alpha (hybrid): Balance keyword vs semantic
    """)
