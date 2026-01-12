"""
Practical RAG with File Loading
Demonstrates RAG with actual PDF, TXT, and DOCX files

Install required packages:
pip install pypdf2 python-docx sentence-transformers

This shows how to:
1. Load documents from various file formats
2. Apply RAG to real files
3. Handle multiple documents
4. Save/load embeddings for reuse
"""

import os
import pickle
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

# File format handlers
try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️  PyPDF2 not installed. Install with: pip install pypdf2")

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("⚠️  python-docx not installed. Install with: pip install python-docx")

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("⚠️  sentence-transformers not installed. Install with: pip install sentence-transformers numpy")

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise RuntimeError("ANTHROPIC_API_KEY not set.")

client = Anthropic(api_key=api_key)
MODEL = "claude-3-5-haiku-latest"


# =========================
# DOCUMENT LOADERS
# =========================

class DocumentLoader:
    """Load documents from various file formats"""
    
    @staticmethod
    def load_txt(filepath: str) -> str:
        """Load plain text file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def load_pdf(filepath: str) -> str:
        """Load PDF file"""
        if not PDF_AVAILABLE:
            raise RuntimeError("PyPDF2 required. Install with: pip install pypdf2")
        
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        return text
    
    @staticmethod
    def load_docx(filepath: str) -> str:
        """Load DOCX file"""
        if not DOCX_AVAILABLE:
            raise RuntimeError("python-docx required. Install with: pip install python-docx")
        
        doc = DocxDocument(filepath)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    
    @staticmethod
    def load_file(filepath: str) -> Tuple[str, str]:
        """Auto-detect and load file based on extension"""
        path = Path(filepath)
        extension = path.suffix.lower()
        
        if extension == '.txt':
            content = DocumentLoader.load_txt(filepath)
        elif extension == '.pdf':
            content = DocumentLoader.load_pdf(filepath)
        elif extension == '.docx':
            content = DocumentLoader.load_docx(filepath)
        else:
            raise ValueError(f"Unsupported file type: {extension}")
        
        return content, path.name


# =========================
# PERSISTENT RAG SYSTEM
# =========================

class PersistentRAG:
    """
    RAG system that can save/load embeddings to avoid recomputing
    Perfect for production use where you preprocess once
    """
    
    def __init__(self, cache_dir: str = "./rag_cache"):
        if not EMBEDDINGS_AVAILABLE:
            raise RuntimeError("sentence-transformers required")
        
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.documents: Dict[str, str] = {}
        self.chunks: List[Dict] = []
        self.embeddings: Optional[np.ndarray] = None
    
    def add_document(self, filepath: str, doc_id: Optional[str] = None):
        """Add a document to the RAG system"""
        content, filename = DocumentLoader.load_file(filepath)
        doc_id = doc_id or filename
        
        self.documents[doc_id] = content
        print(f"✅ Loaded: {filename} ({len(content)} chars)")
    
    def chunk_documents(self, chunk_size: int = 500, overlap: int = 50):
        """Chunk all documents"""
        self.chunks = []
        
        for doc_id, content in self.documents.items():
            # Simple fixed-size chunking
            start = 0
            chunk_idx = 0
            
            while start < len(content):
                end = start + chunk_size
                chunk_text = content[start:end]
                
                if chunk_text.strip():
                    self.chunks.append({
                        "doc_id": doc_id,
                        "chunk_idx": chunk_idx,
                        "content": chunk_text.strip(),
                        "start": start,
                        "end": min(end, len(content))
                    })
                    chunk_idx += 1
                
                start = end - overlap
        
        print(f"📄 Created {len(self.chunks)} chunks from {len(self.documents)} documents")
    
    def create_embeddings(self):
        """Generate embeddings for all chunks"""
        if not self.chunks:
            raise RuntimeError("Must chunk documents first")
        
        texts = [chunk['content'] for chunk in self.chunks]
        print(f"🔄 Generating embeddings...")
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        print(f"✅ Generated embeddings: {self.embeddings.shape}")
    
    def save_index(self, index_name: str = "default"):
        """Save chunks and embeddings to disk"""
        index_path = self.cache_dir / f"{index_name}.pkl"
        
        data = {
            "chunks": self.chunks,
            "embeddings": self.embeddings,
            "documents": self.documents
        }
        
        with open(index_path, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"💾 Saved index to: {index_path}")
    
    def load_index(self, index_name: str = "default"):
        """Load chunks and embeddings from disk"""
        index_path = self.cache_dir / f"{index_name}.pkl"
        
        if not index_path.exists():
            raise FileNotFoundError(f"Index not found: {index_path}")
        
        with open(index_path, 'rb') as f:
            data = pickle.load(f)
        
        self.chunks = data["chunks"]
        self.embeddings = data["embeddings"]
        self.documents = data["documents"]
        
        print(f"📂 Loaded index from: {index_path}")
        print(f"   Documents: {len(self.documents)}")
        print(f"   Chunks: {len(self.chunks)}")
    
    def search(self, query: str, top_k: int = 3, filter_doc: Optional[str] = None) -> List[Tuple[Dict, float]]:
        """Search for relevant chunks"""
        if self.embeddings is None:
            raise RuntimeError("Must create or load embeddings first")
        
        # Encode query
        query_embedding = self.model.encode([query])[0]
        
        # Calculate similarities
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Filter by document if specified
        if filter_doc:
            valid_indices = [i for i, chunk in enumerate(self.chunks) if chunk['doc_id'] == filter_doc]
            filtered_similarities = [(i, similarities[i]) for i in valid_indices]
            filtered_similarities.sort(key=lambda x: x[1], reverse=True)
            top_indices = [i for i, _ in filtered_similarities[:top_k]]
        else:
            top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = [(self.chunks[idx], float(similarities[idx])) for idx in top_indices]
        return results
    
    def query(self, question: str, top_k: int = 3, filter_doc: Optional[str] = None) -> str:
        """Answer a question using RAG"""
        # Search for relevant chunks
        results = self.search(question, top_k=top_k, filter_doc=filter_doc)
        
        # Build context
        context_parts = []
        for chunk, score in results:
            context_parts.append(
                f"[Source: {chunk['doc_id']}, Relevance: {score:.2f}]\n{chunk['content']}"
            )
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Create prompt
        prompt = f"""You are a helpful assistant. Answer the question based on the provided document excerpts.

Document Excerpts:
{context}

Question: {question}

Provide a clear answer based on the information given. If the information is insufficient, say so."""
        
        # Get answer from Claude
        message = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text


# =========================
# USAGE EXAMPLES
# =========================

def example_with_text_files():
    """Example: RAG with text files"""
    print("\n" + "="*80)
    print("EXAMPLE: RAG WITH TEXT FILES")
    print("="*80)
    
    if not EMBEDDINGS_AVAILABLE:
        print("⚠️  Skipping: sentence-transformers not installed")
        return
    
    # Create sample text files for demo
    os.makedirs("./sample_docs", exist_ok=True)
    
    # Sample document 1
    with open("./sample_docs/product_spec.txt", "w") as f:
        f.write("""
Product Specification: SmartWidget Pro

Overview:
SmartWidget Pro is our flagship product designed for enterprise customers.
It features AI-powered analytics and real-time monitoring capabilities.

Technical Specifications:
- Processing: Quad-core ARM processor
- Memory: 4GB RAM
- Storage: 64GB flash storage
- Connectivity: WiFi 6, Bluetooth 5.0, Ethernet
- Power: 12V DC, 2A

Features:
- Real-time data analytics
- Cloud integration with AWS and Azure
- Mobile app for iOS and Android
- RESTful API for custom integrations
- 99.9% uptime SLA

Pricing:
- Standard Edition: $299/year
- Enterprise Edition: $999/year
- Volume discounts available for 10+ units
        """)
    
    # Sample document 2
    with open("./sample_docs/user_manual.txt", "w") as f:
        f.write("""
SmartWidget Pro - User Manual

Getting Started:
1. Unbox your SmartWidget Pro
2. Connect power adapter
3. Download mobile app from App Store or Google Play
4. Follow in-app setup wizard

Initial Configuration:
- Connect to your WiFi network
- Create an account or sign in
- Configure notification preferences
- Set up integrations (optional)

Daily Operations:
The device runs automatically once configured. Check the dashboard
for real-time metrics and analytics.

Troubleshooting:
- Device not connecting? Reset WiFi settings
- App not loading? Clear cache and restart
- Data not syncing? Check internet connection

Support:
For technical support, contact support@smartwidget.com or call 1-800-WIDGET
        """)
    
    # Initialize RAG
    rag = PersistentRAG()
    
    # Add documents
    rag.add_document("./sample_docs/product_spec.txt")
    rag.add_document("./sample_docs/user_manual.txt")
    
    # Process documents
    rag.chunk_documents(chunk_size=300, overlap=50)
    rag.create_embeddings()
    
    # Save for later use
    rag.save_index("smartwidget_docs")
    
    # Query the system
    questions = [
        "What are the technical specifications?",
        "How much does it cost?",
        "How do I troubleshoot connection issues?",
    ]
    
    for question in questions:
        print(f"\n{'='*80}")
        print(f"Q: {question}")
        print('='*80)
        answer = rag.query(question, top_k=2)
        print(f"\nA: {answer}")


def example_load_existing_index():
    """Example: Load pre-built index"""
    print("\n" + "="*80)
    print("EXAMPLE: LOADING EXISTING INDEX")
    print("="*80)
    
    if not EMBEDDINGS_AVAILABLE:
        print("⚠️  Skipping: sentence-transformers not installed")
        return
    
    try:
        # Load existing index (much faster than rebuilding)
        rag = PersistentRAG()
        rag.load_index("smartwidget_docs")
        
        # Query immediately
        question = "What cloud platforms are supported?"
        print(f"\nQ: {question}")
        answer = rag.query(question, top_k=2)
        print(f"\nA: {answer}")
        
    except FileNotFoundError:
        print("❌ Index not found. Run example_with_text_files() first.")


def example_multi_document_search():
    """Example: Search across multiple documents"""
    print("\n" + "="*80)
    print("EXAMPLE: MULTI-DOCUMENT SEARCH")
    print("="*80)
    
    if not EMBEDDINGS_AVAILABLE:
        print("⚠️  Skipping: sentence-transformers not installed")
        return
    
    try:
        rag = PersistentRAG()
        rag.load_index("smartwidget_docs")
        
        # Search in specific document
        question = "How do I set up the device?"
        print(f"\nQ: {question}")
        print("\n📋 Searching only in user_manual.txt:")
        answer = rag.query(question, top_k=2, filter_doc="user_manual.txt")
        print(f"\nA: {answer}")
        
        # Search across all documents
        print("\n📋 Searching across all documents:")
        answer = rag.query(question, top_k=2)
        print(f"\nA: {answer}")
        
    except FileNotFoundError:
        print("❌ Index not found. Run example_with_text_files() first.")


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    if not EMBEDDINGS_AVAILABLE:
        print("\n" + "="*80)
        print("SETUP REQUIRED")
        print("="*80)
        print("\nInstall required packages:")
        print("  pip install sentence-transformers numpy pypdf2 python-docx")
        print("="*80)
    else:
        # Run examples
        example_with_text_files()
        
        print("\n\n")
        example_load_existing_index()
        
        print("\n\n")
        example_multi_document_search()
    
    print("\n" + "="*80)
    print("PRODUCTION TIPS")
    print("="*80)
    print("""
1. PREPROCESSING:
   - Process documents once, save embeddings
   - Use rag.save_index() to persist
   - Load with rag.load_index() for fast queries

2. CHUNKING STRATEGY:
   - Tune chunk_size based on your documents
   - Use overlap to prevent splitting related content
   - Consider semantic chunking for structured docs

3. SCALING:
   - For large document sets, use vector database (Pinecone, Weaviate)
   - Batch process documents during off-peak hours
   - Use metadata for filtering (date, category, source)

4. MONITORING:
   - Track retrieval accuracy
   - Measure answer quality
   - Monitor costs and latency

5. OPTIMIZATION:
   - Cache frequently asked questions
   - Use smaller embedding models for speed
   - Implement query expansion for better retrieval
    """)
