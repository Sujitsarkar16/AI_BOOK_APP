"""
RAG (Retrieval-Augmented Generation) service using Chroma vector database
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class RAGService:
    """Service for managing vector embeddings and retrieval"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize Chroma client and embedding model"""
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def get_or_create_collection(self, book_id: int):
        """Get or create a collection for a book"""
        collection_name = f"book_{book_id}"
        try:
            collection = self.client.get_collection(name=collection_name)
        except:
            collection = self.client.create_collection(name=collection_name)
        return collection
    
    def add_documents(self, book_id: int, documents: List[str], metadata: List[Dict[str, Any]]):
        """
        Add documents to the vector store
        
        Args:
            book_id: Book ID
            documents: List of document chunks (text)
            metadata: List of metadata dicts for each document
        """
        try:
            collection = self.get_or_create_collection(book_id)
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(documents).tolist()
            
            # Create IDs
            doc_ids = [f"doc_{book_id}_{i}" for i in range(len(documents))]
            
            # Add to collection
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadata,
                ids=doc_ids
            )
            
            logger.info(f"Added {len(documents)} documents to book_{book_id}")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search_relevant_context(self, book_id: int, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant context
        
        Args:
            book_id: Book ID
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            collection = self.get_or_create_collection(book_id)
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format results
            documents = results['documents'][0] if results['documents'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            
            context = [
                {
                    'text': doc,
                    'metadata': meta
                }
                for doc, meta in zip(documents, metadatas)
            ]
            
            return context
        except Exception as e:
            logger.error(f"Error searching context: {e}")
            return []
    
    def delete_book_documents(self, book_id: int):
        """Delete all documents for a book"""
        try:
            collection_name = f"book_{book_id}"
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection for book_{book_id}")
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")


# Global instance
rag_service = RAGService()

