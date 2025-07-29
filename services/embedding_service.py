import openai
import os
import numpy as np
import faiss
from typing import List, Dict, Any
import logging
import pickle
from sentence_transformers import SentenceTransformer
import time

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Handles embedding generation and storage using OpenAI and FAISS"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
        self.embedding_model = "text-embedding-ada-002"
        self.faiss_index = None
        self.document_segments = []
        self.embeddings_cache = {}
        
        # Initialize OpenAI client
        openai.api_key = self.api_key
        
        # Fallback to sentence transformers if OpenAI is not available
        try:
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.warning(f"Could not load sentence transformer: {e}")
            self.sentence_transformer = None
    
    async def initialize(self):
        """Initialize the embedding service"""
        try:
            # Test OpenAI connection
            await self._test_openai_connection()
            logger.info("Embedding service initialized with OpenAI")
        except Exception as e:
            logger.warning(f"OpenAI not available, using sentence transformers: {e}")
    
    async def generate_embeddings(self, document_segments: List[Dict[str, Any]]) -> List[np.ndarray]:
        """
        Generate embeddings for document segments
        """
        try:
            embeddings = []
            texts = [segment["text"] for segment in document_segments]
            
            # Generate embeddings
            if self.api_key != "your-openai-api-key":
                embeddings = await self._generate_openai_embeddings(texts)
            else:
                embeddings = self._generate_sentence_transformer_embeddings(texts)
            
            # Store segments for later retrieval
            self.document_segments = document_segments
            
            # Create FAISS index
            await self._create_faiss_index(embeddings)
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    async def find_similar_segments(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find most similar document segments using FAISS
        """
        try:
            if self.faiss_index is None:
                raise ValueError("FAISS index not initialized")
            
            # Search for similar vectors
            query_embedding = query_embedding.reshape(1, -1).astype('float32')
            distances, indices = self.faiss_index.search(query_embedding, top_k)
            
            results = []
            for i, (distance, index) in enumerate(zip(distances[0], indices[0])):
                if index < len(self.document_segments):
                    segment = self.document_segments[index]
                    confidence = 1.0 / (1.0 + distance)  # Convert distance to confidence
                    
                    result = {
                        "segment": segment,
                        "distance": float(distance),
                        "confidence": float(confidence),
                        "rank": i + 1
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar segments: {str(e)}")
            return []
    
    async def _generate_openai_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings using OpenAI API"""
        try:
            embeddings = []
            
            # Process in batches to avoid rate limits
            batch_size = 10
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = openai.Embedding.create(
                    input=batch,
                    model=self.embedding_model
                )
                
                batch_embeddings = [np.array(embedding.embedding) for embedding in response.data]
                embeddings.extend(batch_embeddings)
                
                # Small delay to avoid rate limits
                time.sleep(0.1)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating OpenAI embeddings: {str(e)}")
            raise
    
    def _generate_sentence_transformer_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings using sentence transformers"""
        try:
            if self.sentence_transformer is None:
                raise ValueError("Sentence transformer not available")
            
            embeddings = self.sentence_transformer.encode(texts, convert_to_numpy=True)
            return [embedding for embedding in embeddings]
            
        except Exception as e:
            logger.error(f"Error generating sentence transformer embeddings: {str(e)}")
            raise
    
    async def _create_faiss_index(self, embeddings: List[np.ndarray]):
        """Create FAISS index for efficient similarity search"""
        try:
            if not embeddings:
                return
            
            # Convert to numpy array
            embeddings_array = np.array(embeddings).astype('float32')
            dimension = embeddings_array.shape[1]
            
            # Create FAISS index
            self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            self.faiss_index.add(embeddings_array)
            
            logger.info(f"Created FAISS index with {len(embeddings)} vectors")
            
        except Exception as e:
            logger.error(f"Error creating FAISS index: {str(e)}")
            raise
    
    async def _test_openai_connection(self):
        """Test OpenAI API connection"""
        try:
            test_response = openai.Embedding.create(
                input=["test"],
                model=self.embedding_model
            )
            return True
        except Exception as e:
            logger.warning(f"OpenAI connection test failed: {e}")
            return False
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        if self.faiss_index:
            return self.faiss_index.d
        return 1536  # Default OpenAI embedding dimension
    
    async def close(self):
        """Cleanup resources"""
        self.faiss_index = None
        self.document_segments = []
        self.embeddings_cache = {}
        logger.info("Embedding service closed") 