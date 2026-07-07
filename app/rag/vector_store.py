import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from app.config.settings import settings
from app.core.logging import logger

# Try importing sentence_transformers
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    logger.warning("sentence-transformers not found. Falling back to keyword-based matching for RAG.")

# Try importing chromadb
try:
    import chromadb
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    logger.warning("chromadb not found. Falling back to local file-based Vector Store.")


class BaseVectorStore:
    """Interface for Vector Store implementations."""
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        raise NotImplementedError
        
    def query(self, query_text: str, top_k: int = 3, metadata_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError


class InMemoryVectorStore(BaseVectorStore):
    """
    Pure Python fallback Vector Store. Uses sentence-transformers if available,
    otherwise uses clean keyword intersection scoring.
    """
    def __init__(self, db_dir: str):
        self.db_dir = db_dir
        self.index_file = os.path.join(db_dir, "in_memory_index.json")
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: List[List[float]] = []
        
        # Load embedding model if available
        self.model = None
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
                self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            except Exception as e:
                logger.error(f"Failed to load sentence-transformers model: {e}. Using keyword matching.")
        
        self.load_index()

    def load_index(self) -> None:
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir, exist_ok=True)
            return
            
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.documents = data.get("documents", [])
                    self.embeddings = data.get("embeddings", [])
                logger.info(f"Loaded {len(self.documents)} documents from fallback index: {self.index_file}")
            except Exception as e:
                logger.error(f"Error loading fallback index file: {e}")

    def save_index(self) -> None:
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump({
                    "documents": self.documents,
                    "embeddings": self.embeddings
                }, f, indent=2)
            logger.info(f"Saved fallback index to {self.index_file}")
        except Exception as e:
            logger.error(f"Error saving fallback index: {e}")

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Expects list of dicts with:
        - content: str
        - metadata: dict
        """
        new_docs = []
        new_texts = []
        
        for idx, doc in enumerate(documents):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            if not content:
                continue
            
            # Format document object
            doc_obj = {
                "id": f"doc_{len(self.documents) + len(new_docs)}",
                "content": content,
                "metadata": metadata
            }
            new_docs.append(doc_obj)
            new_texts.append(content)
            
        if not new_docs:
            return
            
        if self.model and HAS_SENTENCE_TRANSFORMERS:
            try:
                # Compute embeddings
                embeddings = self.model.encode(new_texts).tolist()
                self.embeddings.extend(embeddings)
            except Exception as e:
                logger.error(f"Error calculating embeddings: {e}")
                # Fill dummy embeddings if fail
                self.embeddings.extend([[0.0] * 384] * len(new_docs))
        else:
            # Fill dummy embeddings if no model
            self.embeddings.extend([[0.0] * 384] * len(new_docs))
            
        self.documents.extend(new_docs)
        self.save_index()

    def query(self, query_text: str, top_k: int = 3, metadata_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self.documents:
            return []
            
        # Filter documents first if metadata_filter is provided
        candidate_indices = []
        for idx, doc in enumerate(self.documents):
            match = True
            if metadata_filter:
                for k, v in metadata_filter.items():
                    if doc["metadata"].get(k) != v:
                        match = False
                        break
            if match:
                candidate_indices.append(idx)
                
        if not candidate_indices:
            return []
            
        scores = []
        if self.model and HAS_SENTENCE_TRANSFORMERS and self.embeddings and any(any(val != 0.0 for val in emb) for emb in self.embeddings):
            try:
                query_emb = self.model.encode(query_text)
                for idx in candidate_indices:
                    doc_emb = np.array(self.embeddings[idx])
                    # Cosine similarity
                    denom = (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb))
                    sim = np.dot(query_emb, doc_emb) / denom if denom > 0 else 0.0
                    scores.append((idx, float(sim)))
            except Exception as e:
                logger.error(f"Fallback query embedding calculation failed: {e}. Defaulting to keyword matching.")
                scores = self._query_keyword_matching(query_text, candidate_indices)
        else:
            scores = self._query_keyword_matching(query_text, candidate_indices)
            
        # Sort and take top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in scores[:top_k]:
            results.append({
                "content": self.documents[idx]["content"],
                "metadata": self.documents[idx]["metadata"],
                "score": score
            })
        return results

    def _query_keyword_matching(self, query_text: str, indices: List[int]) -> List[tuple]:
        query_words = set(query_text.lower().split())
        scores = []
        for idx in indices:
            content = self.documents[idx]["content"].lower()
            # Simple word overlap count as match score
            matches = sum(1 for word in query_words if word in content)
            scores.append((idx, float(matches)))
        return scores

    def clear(self) -> None:
        self.documents = []
        self.embeddings = []
        if os.path.exists(self.index_file):
            try:
                os.remove(self.index_file)
            except Exception as e:
                logger.error(f"Error removing fallback index file: {e}")
        logger.info("Cleared local fallback Vector Store.")


class ChromaVectorStore(BaseVectorStore):
    """Production-grade Vector Store using ChromaDB."""
    def __init__(self, db_dir: str):
        self.db_dir = db_dir
        self.client = chromadb.PersistentClient(path=db_dir)
        
        # Load embedding model if available
        self.model = None
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
                self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            except Exception as e:
                logger.error(f"Failed to load sentence-transformers model in Chroma: {e}")
                
        # Custom embedding function wrapper for Chroma
        class CustomEmbeddingFunction(chromadb.EmbeddingFunction):
            def __init__(self, model):
                self.model = model
            def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
                if self.model:
                    return self.model.encode(input).tolist()
                return [[0.0] * 384] * len(input)

        emb_fn = CustomEmbeddingFunction(self.model) if self.model else None
        self.collection = self.client.get_or_create_collection(
            name="enterprise_knowledge",
            embedding_function=emb_fn
        )
        logger.info("ChromaDB vector store initialized successfully.")

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        ids = []
        contents = []
        metadatas = []
        
        for idx, doc in enumerate(documents):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            if not content:
                continue
            
            # Chroma requires flat metadatas (string, int, float, bool)
            flat_metadata = {}
            for k, v in metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    flat_metadata[k] = v
                elif isinstance(v, list):
                    flat_metadata[k] = ", ".join(map(str, v))
                else:
                    flat_metadata[k] = str(v)
                    
            ids.append(f"chroma_doc_{self.collection.count() + idx}")
            contents.append(content)
            metadatas.append(flat_metadata)
            
        if ids:
            self.collection.add(ids=ids, documents=contents, metadatas=metadatas)
            logger.info(f"Added {len(ids)} documents to ChromaDB.")

    def query(self, query_text: str, top_k: int = 3, metadata_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # Map metadata filter
        where_clause = None
        if metadata_filter:
            where_clause = {}
            for k, v in metadata_filter.items():
                if isinstance(v, (str, int, float, bool)):
                    where_clause[k] = v
                else:
                    where_clause[k] = str(v)
                    
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k,
            where=where_clause
        )
        
        formatted = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(docs)
            
            for doc, meta, dist in zip(docs, metas, distances):
                formatted.append({
                    "content": doc,
                    "metadata": meta,
                    "score": float(1.0 - dist)  # Map distance to similarity score
                })
        return formatted

    def clear(self) -> None:
        self.client.delete_collection("enterprise_knowledge")
        self.collection = self.client.get_or_create_collection(name="enterprise_knowledge")
        logger.info("Cleared ChromaDB collection.")


# Factory/Singleton selection
def get_vector_store() -> BaseVectorStore:
    db_dir = settings.VECTOR_DB_DIR
    if HAS_CHROMADB:
        try:
            return ChromaVectorStore(db_dir)
        except Exception as e:
            logger.error(f"Error initializing ChromaDB Vector Store: {e}. Falling back to InMemoryVectorStore.")
            return InMemoryVectorStore(db_dir)
    else:
        return InMemoryVectorStore(db_dir)

# Global Vector Store Instance
vector_store = get_vector_store()
