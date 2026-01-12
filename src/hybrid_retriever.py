"""
Hybrid Retrieval System
Combines Semantic Search (Vector Index) and Lexical Search (BM25)
using Reciprocal Rank Fusion for improved RAG results.

Based on Anthropic Course: 005 Hybrid Search
"""

import re
import math
from typing import List, Tuple, Dict, Any


class SimpleVectorIndex:
    """Simple in-memory vector index for semantic search using cosine similarity."""
    
    def __init__(self):
        self.vectors = []
        self.metadata = []
    
    def add_document(self, embedding: List[float], metadata: Dict[str, Any]):
        """Add a document with its embedding to the index."""
        self.vectors.append(embedding)
        self.metadata.append(metadata)
    
    def search(self, query_embedding: List[float], top_k: int = 2) -> List[Tuple[Dict, float]]:
        """Search for most similar vectors using cosine similarity.
        
        Returns list of (metadata, distance) tuples where distance is cosine distance.
        """
        if not self.vectors:
            return []
        
        results = []
        
        for i, stored_embedding in enumerate(self.vectors):
            # Cosine similarity = dot product / (magnitude1 * magnitude2)
            dot_product = sum(a * b for a, b in zip(query_embedding, stored_embedding))
            magnitude_query = sum(x * x for x in query_embedding) ** 0.5
            magnitude_stored = sum(x * x for x in stored_embedding) ** 0.5
            
            if magnitude_query == 0 or magnitude_stored == 0:
                cosine_similarity = 0
            else:
                cosine_similarity = dot_product / (magnitude_query * magnitude_stored)
            
            # Cosine distance = 1 - similarity
            cosine_distance = 1 - cosine_similarity
            
            results.append((self.metadata[i], cosine_distance))
        
        # Sort by distance (ascending - closest first)
        results.sort(key=lambda x: x[1])
        return results[:top_k]


class BM25Index:
    """BM25 lexical search index for keyword-based retrieval.
    
    BM25 (Best Match 25) is a ranking function used in information retrieval.
    It scores chunks based on term frequency and term importance.
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """Initialize BM25 index.
        
        Args:
            k1: Controls term frequency saturation (default 1.5)
            b: Controls length normalization (default 0.75)
        """
        self.k1 = k1
        self.b = b
        self.documents = []
        self.metadata = []
        self.idf = {}  # Inverse Document Frequency
        self.doc_lengths = []
        self.avg_doc_length = 0
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into lowercase words, removing punctuation."""
        text = text.lower()
        # Remove punctuation and split by whitespace
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def add_document(self, text: str, metadata: Dict[str, Any]):
        """Add a document to the BM25 index."""
        tokens = self._tokenize(text)
        self.documents.append(tokens)
        self.metadata.append(metadata)
        self.doc_lengths.append(len(tokens))
        
        # Update IDF for all tokens
        for token in set(tokens):
            if token not in self.idf:
                self.idf[token] = 0
            self.idf[token] += 1
        
        # Update average document length
        if self.doc_lengths:
            self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths)
    
    def _calculate_idf(self, token: str) -> float:
        """Calculate IDF (Inverse Document Frequency) for a token."""
        if token not in self.idf:
            return 0
        
        num_docs = len(self.documents)
        doc_freq = self.idf[token]
        
        # BM25 IDF formula
        idf = math.log((num_docs - doc_freq + 0.5) / (doc_freq + 0.5) + 1)
        return idf
    
    def _score_document(self, doc_idx: int, tokens: List[str]) -> float:
        """Calculate BM25 score for a document given query tokens."""
        score = 0
        doc = self.documents[doc_idx]
        doc_length = self.doc_lengths[doc_idx]
        
        for token in tokens:
            if token not in doc:
                continue
            
            # Term frequency in document
            term_freq = doc.count(token)
            
            # IDF for this term
            idf = self._calculate_idf(token)
            
            # BM25 formula
            numerator = idf * term_freq * (self.k1 + 1)
            denominator = term_freq + self.k1 * (1 - self.b + self.b * (doc_length / (self.avg_doc_length + 0.001)))
            
            score += numerator / denominator
        
        return score
    
    def search(self, query: str, top_k: int = 2) -> List[Tuple[Dict, float]]:
        """Search for most relevant documents using BM25.
        
        Returns list of (metadata, distance) tuples where distance is negative score
        (to match vector index format where lower is better).
        """
        if not self.documents:
            return []
        
        tokens = self._tokenize(query)
        if not tokens:
            return []
        
        results = []
        
        for doc_idx in range(len(self.documents)):
            score = self._score_document(doc_idx, tokens)
            # Use negative score as distance so lower is better (matching vector index)
            results.append((self.metadata[doc_idx], -score))
        
        # Sort by distance (ascending - best matches first)
        results.sort(key=lambda x: x[1])
        return results[:top_k]


class Retriever:
    """Hybrid retriever combining semantic and lexical search via Reciprocal Rank Fusion."""
    
    def __init__(self):
        """Initialize retriever with both search indexes."""
        self.vector_index = SimpleVectorIndex()
        self.bm25_index = BM25Index()
    
    def add_document(self, text: str, embedding: List[float], metadata: Dict[str, Any]):
        """Add a document to both indexes.
        
        Args:
            text: Document text for lexical search
            embedding: Embedding vector for semantic search
            metadata: Document metadata (content, source, etc)
        """
        self.vector_index.add_document(embedding, metadata)
        self.bm25_index.add_document(text, metadata)
    
    def _reciprocal_rank_fusion(self, results_list: List[List[Tuple[Dict, float]]], k: int = 60) -> List[Tuple[Dict, float]]:
        """Merge results from multiple search systems using Reciprocal Rank Fusion.
        
        RRF formula: score = sum(1 / (k + rank)) for each ranking
        
        Args:
            results_list: List of result lists from different search systems
            k: Constant for RRF (default 60, typical value)
        
        Returns:
            Merged and ranked results
        """
        # Create a dictionary to track all unique documents and their ranks
        doc_scores = {}
        
        for results in results_list:
            for rank, (metadata, _) in enumerate(results, 1):
                doc_id = id(metadata)  # Use object id as unique identifier
                
                if doc_id not in doc_scores:
                    doc_scores[doc_id] = {'metadata': metadata, 'score': 0}
                
                # RRF: 1 / (k + rank)
                rrf_score = 1 / (k + rank)
                doc_scores[doc_id]['score'] += rrf_score
        
        # Sort by RRF score (descending)
        sorted_results = sorted(
            doc_scores.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        # Return as list of (metadata, distance) tuples
        # Use negative score as distance so lower is "better"
        return [(doc['metadata'], -doc['score']) for doc in sorted_results]
    
    def search(self, query: str, query_embedding: List[float], top_k: int = 2) -> List[Tuple[Dict, float]]:
        """Search using both semantic and lexical search, merged via RRF.
        
        Args:
            query: User's text query
            query_embedding: Embedding of the query
            top_k: Number of results to return
        
        Returns:
            List of (metadata, score) tuples, ranked by RRF
        """
        # Get results from both search systems
        vector_results = self.vector_index.search(query_embedding, top_k=top_k)
        bm25_results = self.bm25_index.search(query, top_k=top_k)
        
        # Merge using Reciprocal Rank Fusion
        merged_results = self._reciprocal_rank_fusion([vector_results, bm25_results])
        
        return merged_results[:top_k]


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts.
    
    Tries to use sentence-transformers, falls back to simulated embeddings.
    """
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(texts, show_progress_bar=False)
        return [embedding.tolist() for embedding in embeddings]
    except ImportError:
        # Simulated embeddings based on text features
        embeddings = []
        for text in texts:
            text_lower = text.lower()
            
            medical_score = sum([
                text_lower.count('medical'),
                text_lower.count('health'),
                text_lower.count('patient'),
                text_lower.count('research')
            ]) / max(len(text), 1) * 1000
            
            software_score = sum([
                text_lower.count('software'),
                text_lower.count('engineer'),
                text_lower.count('bug'),
                text_lower.count('incident')
            ]) / max(len(text), 1) * 1000
            
            business_score = sum([
                text_lower.count('revenue'),
                text_lower.count('profit'),
                text_lower.count('business'),
                text_lower.count('market')
            ]) / max(len(text), 1) * 1000
            
            total = medical_score + software_score + business_score + 0.001
            embedding = [
                medical_score / total,
                software_score / total,
                business_score / total
            ]
            
            embeddings.append(embedding)
        
        return embeddings


def chunk_text_by_section(text: str) -> List[str]:
    """Chunk text by markdown sections."""
    pattern = r'\n(?=## )'
    chunks = re.split(pattern, text)
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def add_contextual_retrieval(chunk: str, source_text: str, client, starter_chunks: int = 2, nearby_chunks: int = 2, all_chunks: List[str] = None, chunk_index: int = None) -> str:
    """Add context to a chunk using Claude (Contextual Retrieval technique from Lesson 007).
    
    This preprocessing step adds situating context to each chunk before indexing.
    The added context helps retrieval by providing ties to the larger document.
    
    Args:
        chunk: The text chunk to add context to
        source_text: Full source document text (if document fits in context)
        client: Anthropic client for calling Claude
        starter_chunks: Number of chunks from document start to include (default 2)
        nearby_chunks: Number of chunks before target to include (default 2)
        all_chunks: List of all chunks (needed for large document strategy)
        chunk_index: Index of current chunk in all_chunks (needed for large document strategy)
    
    Returns:
        Contextualized chunk = [Claude's context] + [original chunk]
    
    Strategy for Large Documents:
    If source document is too large, include:
    - Starter chunks (intro/abstract) 
    - Nearby chunks (immediate context)
    This reduces prompt size while preserving relevant context.
    """
    if not client:
        print("[WARNING] Contextual retrieval requires Anthropic client. Returning original chunk.")
        return chunk
    
    # Determine context to send to Claude
    if all_chunks and chunk_index is not None:
        # Large document strategy: use starter + nearby chunks
        context_chunks = []
        
        # Add starter chunks (intro/summary)
        for i in range(min(starter_chunks, len(all_chunks))):
            if i != chunk_index:
                context_chunks.append(all_chunks[i])
        
        # Add nearby chunks (before target)
        start_idx = max(0, chunk_index - nearby_chunks)
        for i in range(start_idx, chunk_index):
            if all_chunks[i] not in context_chunks:
                context_chunks.append(all_chunks[i])
        
        context_text = "\n\n".join(context_chunks)
    else:
        # Small document: use full source
        context_text = source_text
    
    # Prompt Claude to generate situating context
    prompt = f"""Here is a chunk from a larger document:

<chunk>
{chunk}
</chunk>

Here is context from the larger document:

<document>
{context_text}
</document>

Please write a short, succinct context (2-3 sentences) to situate this chunk within the overall document. This context will help with retrieval later.

Focus on:
- What section/topic this chunk covers
- How it relates to other sections
- Key concepts or entities mentioned

Context:"""
    
    try:
        response = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        added_context = response.content[0].text.strip()
        
        # Return contextualized chunk: [context] + [original]
        return f"{added_context}\n\n{chunk}"
    
    except Exception as e:
        print(f"[WARNING] Failed to add context: {e}. Returning original chunk.")
        return chunk


class RetrieverWithReranking(Retriever):
    """Extended Retriever with Claude-based re-ranking for improved accuracy.
    
    Adds a post-processing step that uses Claude to re-order search results
    based on relevance to the user's query. This improves accuracy at the cost
    of increased latency (requires an additional Claude API call).
    """
    
    def __init__(self, client=None):
        """Initialize retriever with optional Anthropic client for re-ranking.
        
        Args:
            client: Anthropic client instance (required for re-ranking)
        """
        super().__init__()
        self.client = client
    
    def _format_documents_for_reranking(self, results: List[Tuple[Dict, float]]) -> str:
        """Format search results as XML for Claude re-ranking prompt.
        
        Args:
            results: List of (metadata, score) tuples from hybrid search
        
        Returns:
            XML-formatted string of documents with IDs
        """
        xml_docs = []
        for i, (metadata, score) in enumerate(results, 1):
            doc_id = f"doc_{i}"
            content = metadata.get('content', '')[:500]  # Limit to first 500 chars
            section = metadata.get('section', f'Document {i}')
            
            xml_docs.append(f"""<document id="{doc_id}">
  <section>{section}</section>
  <content>{content}</content>
</document>""")
        
        return "\n".join(xml_docs)
    
    def rerank_with_claude(self, query: str, results: List[Tuple[Dict, float]], top_k: int = 3) -> List[Tuple[Dict, float]]:
        """Re-rank search results using Claude for improved relevance.
        
        Claude analyzes the user's query and the retrieved documents, then returns
        them in order of decreasing relevance. This improves accuracy especially
        for queries with specific terminology or multiple concepts.
        
        Args:
            query: User's original query
            results: Search results from hybrid retrieval
            top_k: Number of top results to return after re-ranking
        
        Returns:
            Re-ranked results as list of (metadata, score) tuples
        """
        if not self.client:
            print("[WARNING] Re-ranking requires Anthropic client. Returning unranked results.")
            return results[:top_k]
        
        if not results:
            return results
        
        # Format documents for Claude
        xml_documents = self._format_documents_for_reranking(results)
        
        # Create re-ranking prompt
        rerank_prompt = f"""You are a document relevance expert. Analyze the user's query and the retrieved documents, then return the document IDs in order of decreasing relevance.

User Query: "{query}"

Retrieved Documents:
{xml_documents}

Task: Return a JSON list of document IDs in order of decreasing relevance (most relevant first).
Return ONLY a valid JSON array with no additional text.

Example format: ["doc_2", "doc_1", "doc_3"]

Your response (JSON array only):"""
        
        try:
            # Call Claude for re-ranking
            response = self.client.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": rerank_prompt
                    }
                ]
            )
            
            # Parse Claude's response
            response_text = response.content[0].text.strip()
            
            # Extract JSON array from response
            import json
            try:
                ranked_ids = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from the response if it contains extra text
                import re as regex_module
                match = regex_module.search(r'\[.*\]', response_text, regex_module.DOTALL)
                if match:
                    ranked_ids = json.loads(match.group())
                else:
                    print(f"[WARNING] Could not parse Claude response: {response_text}")
                    return results[:top_k]
            
            # Re-order results based on Claude's ranking
            reranked_results = []
            doc_id_to_result = {f"doc_{i+1}": (metadata, score) for i, (metadata, score) in enumerate(results)}
            
            for doc_id in ranked_ids:
                if doc_id in doc_id_to_result:
                    reranked_results.append(doc_id_to_result[doc_id])
            
            # Add any remaining results not in Claude's ranking
            for i, (metadata, score) in enumerate(results, 1):
                doc_id = f"doc_{i}"
                if doc_id not in ranked_ids and len(reranked_results) < len(results):
                    reranked_results.append((metadata, score))
            
            return reranked_results[:top_k]
        
        except Exception as e:
            print(f"[WARNING] Re-ranking failed: {str(e)}. Returning unranked results.")
            return results[:top_k]
    
    def search_with_reranking(self, query: str, query_embedding: List[float], top_k: int = 3) -> List[Tuple[Dict, float]]:
        """Search using hybrid retrieval, then re-rank results with Claude.
        
        This combines the benefits of:
        - Vector search (semantic understanding)
        - BM25 search (keyword matching)
        - RRF merging (balanced ranking)
        - Claude re-ranking (relevance refinement)
        
        Args:
            query: User's text query
            query_embedding: Embedding of the query
            top_k: Number of results to return
        
        Returns:
            Re-ranked search results
        """
        # First, run hybrid search (Vector + BM25 + RRF)
        hybrid_results = self.search(query, query_embedding, top_k=top_k * 2)
        
        # Then, re-rank results with Claude
        reranked_results = self.rerank_with_claude(query, hybrid_results, top_k=top_k)
        
        return reranked_results
