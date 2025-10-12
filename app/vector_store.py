# ==============================================================================
# app/vector_store.py
# The Intelligence Vault - Multi-Tenant Vector Store Manager
# ==============================================================================
"""
This module manages the ChromaDB vector store for CLARITY's Intelligence Vault.
Each user gets their own isolated collection for secure, multi-tenant memory storage.

Key Features:
- Multi-tenant architecture (one collection per user)
- Secure isolation between users
- Persistent memory storage
- Embedding generation and similarity search
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Any
import logging
from config import Config

# Configure logging
logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Manages ChromaDB vector store operations for the Intelligence Vault.
    Implements multi-tenant architecture with one collection per user.
    """
    
    def __init__(self):
        """Initialize the ChromaDB client and embedding model."""
        try:
            # Initialize ChromaDB client
            self.client = chromadb.HttpClient(
                host=Config.CHROMA_HOST,
                port=Config.CHROMA_PORT,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=False
                )
            )
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
            
            # Create custom embedding function for ChromaDB
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=Config.EMBEDDING_MODEL
            )
            
            logger.info(f"VectorStoreManager initialized successfully with model: {Config.EMBEDDING_MODEL}")
            
        except Exception as e:
            logger.error(f"Failed to initialize VectorStoreManager: {e}")
            raise
    
    def _get_collection_name(self, user_id: int) -> str:
        """
        Generate a unique collection name for a user.
        
        Args:
            user_id: The user's database ID
            
        Returns:
            Unique collection name for the user
        """
        return f"user_vault_{user_id}"
    
    def get_or_create_user_collection(self, user_id: int):
        """
        Get or create a ChromaDB collection for a specific user.
        This ensures multi-tenant isolation - each user has their own collection.
        
        Args:
            user_id: The user's database ID
            
        Returns:
            ChromaDB collection object for the user
        """
        collection_name = self._get_collection_name(user_id)
        
        try:
            # Try to get existing collection
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Retrieved existing collection for user {user_id}")
            
        except Exception:
            # Collection doesn't exist, create it
            collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={
                    "user_id": str(user_id),
                    "description": f"Intelligence Vault for user {user_id}"
                }
            )
            logger.info(f"Created new collection for user {user_id}")
        
        return collection
    
    def add_documents(
        self,
        user_id: int,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        chunking_strategy: str = 'dynamic'
    ) -> Dict[str, Any]:
        """
        Add documents to a user's Intelligence Vault.
        
        Args:
            user_id: The user's database ID
            documents: List of text chunks to add
            metadatas: Optional list of metadata dicts for each document
            ids: Optional list of unique IDs for each document
            chunking_strategy: Chunking strategy used ('semantic', 'hierarchical', 'context_aware', 'dynamic')
            
        Returns:
            Dict with status and count of documents added
        """
        try:
            collection = self.get_or_create_user_collection(user_id)
            
            # Generate IDs if not provided
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in documents]
            
            # Add default metadata if not provided
            if metadatas is None:
                metadatas = [{"source": "unknown", "chunking_strategy": chunking_strategy} for _ in documents]
            else:
                # Add chunking strategy to existing metadata
                for metadata in metadatas:
                    metadata["chunking_strategy"] = chunking_strategy
            
            # Add documents to collection
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to vault for user {user_id}")
            
            return {
                "success": True,
                "documents_added": len(documents),
                "collection_name": self._get_collection_name(user_id)
            }
            
        except Exception as e:
            logger.error(f"Failed to add documents for user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def query_similar_documents(
        self,
        user_id: int,
        query_text: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for similar documents in a user's Intelligence Vault.
        This is the core of Retrieval-Augmented Generation (RAG).
        
        Args:
            user_id: The user's database ID
            query_text: The text to search for similar documents
            n_results: Number of similar documents to return
            filter_metadata: Optional metadata filter for the search
            
        Returns:
            Dict containing similar documents, distances, and metadata
        """
        try:
            collection = self.get_or_create_user_collection(user_id)
            
            # Perform similarity search
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=filter_metadata
            )
            
            logger.info(f"Retrieved {len(results['documents'][0])} similar documents for user {user_id}")
            
            return {
                "success": True,
                "documents": results['documents'][0] if results['documents'] else [],
                "metadatas": results['metadatas'][0] if results['metadatas'] else [],
                "distances": results['distances'][0] if results['distances'] else [],
                "ids": results['ids'][0] if results['ids'] else []
            }
            
        except Exception as e:
            logger.error(f"Failed to query documents for user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "documents": []
            }
    
    def get_collection_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get statistics about a user's Intelligence Vault.
        
        Args:
            user_id: The user's database ID
            
        Returns:
            Dict with collection statistics
        """
        try:
            collection = self.get_or_create_user_collection(user_id)
            count = collection.count()
            
            return {
                "success": True,
                "collection_name": self._get_collection_name(user_id),
                "document_count": count,
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats for user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_user_collection(self, user_id: int) -> Dict[str, Any]:
        """
        Delete a user's entire Intelligence Vault.
        Use with caution - this is irreversible!
        
        Args:
            user_id: The user's database ID
            
        Returns:
            Dict with deletion status
        """
        collection_name = self._get_collection_name(user_id)
        
        try:
            self.client.delete_collection(name=collection_name)
            logger.warning(f"Deleted collection for user {user_id}")
            
            return {
                "success": True,
                "message": f"Collection {collection_name} deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete collection for user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding vector for a piece of text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            raise


# Global instance
_vector_store = None


def get_vector_store() -> VectorStoreManager:
    """
    Get or create the global VectorStoreManager instance.
    This ensures we reuse the same ChromaDB client and embedding model.
    
    Returns:
        VectorStoreManager instance
    """
    global _vector_store
    
    if _vector_store is None:
        _vector_store = VectorStoreManager()
    
    return _vector_store


# Convenience functions for direct use
def add_to_vault(user_id: int, documents: List[str], metadatas: Optional[List[Dict]] = None) -> Dict:
    """Add documents to a user's vault."""
    store = get_vector_store()
    return store.add_documents(user_id, documents, metadatas)


def search_vault(user_id: int, query: str, n_results: int = 5) -> Dict:
    """Search a user's vault for similar documents."""
    store = get_vector_store()
    return store.query_similar_documents(user_id, query, n_results)


def get_vault_stats(user_id: int) -> Dict:
    """Get statistics about a user's vault."""
    store = get_vector_store()
    return store.get_collection_stats(user_id)
