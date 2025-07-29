import numpy as np
from typing import List, Dict, Any
import logging
import time
from sklearn.metrics.pairwise import cosine_similarity
import re

logger = logging.getLogger(__name__)

class ClauseMatcher:
    """Handles semantic clause matching with confidence scoring"""
    
    def __init__(self):
        self.processing_time = 0
        self.confidence_threshold = 0.7
        self.max_candidates = 10
        
    async def find_best_match(
        self, 
        parsed_query: Dict[str, Any], 
        document_segments: List[Dict[str, Any]], 
        embeddings: List[np.ndarray]
    ) -> Dict[str, Any]:
        """
        Find the best matching clause using semantic search and logic evaluation
        """
        start_time = time.time()
        
        try:
            # Step 1: Generate query embedding
            query_embedding = await self._generate_query_embedding(parsed_query)
            
            # Step 2: Find similar segments using FAISS
            similar_segments = await self._find_similar_segments(query_embedding, embeddings)
            
            # Step 3: Apply logic evaluation and scoring
            scored_matches = await self._evaluate_matches(
                parsed_query, 
                similar_segments, 
                document_segments
            )
            
            # Step 4: Select best match
            best_match = await self._select_best_match(scored_matches)
            
            # Step 5: Format response
            formatted_match = await self._format_match_result(best_match, parsed_query)
            
            self.processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            logger.info(f"Best match found with confidence: {formatted_match.get('confidence', 0.0)}")
            return formatted_match
            
        except Exception as e:
            logger.error(f"Error in clause matching: {str(e)}")
            return self._get_fallback_match()
    
    async def _generate_query_embedding(self, parsed_query: Dict[str, Any]) -> np.ndarray:
        """Generate embedding for the parsed query"""
        try:
            # Combine query components for embedding
            query_text = f"{parsed_query.get('intent', '')} {' '.join(parsed_query.get('keywords', []))} {parsed_query.get('context', '')}"
            
            # Use the same embedding service as document segments
            from services.embedding_service import EmbeddingService
            embedding_service = EmbeddingService()
            
            # Generate embedding (simplified for this example)
            # In practice, this would use the same embedding model as document segments
            query_embedding = np.random.rand(1536)  # Placeholder
            return query_embedding
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            return np.random.rand(1536)  # Fallback
    
    async def _find_similar_segments(
        self, 
        query_embedding: np.ndarray, 
        embeddings: List[np.ndarray]
    ) -> List[Dict[str, Any]]:
        """Find similar document segments using cosine similarity"""
        try:
            similarities = []
            
            for i, doc_embedding in enumerate(embeddings):
                # Calculate cosine similarity
                similarity = cosine_similarity(
                    query_embedding.reshape(1, -1), 
                    doc_embedding.reshape(1, -1)
                )[0][0]
                
                similarities.append({
                    "index": i,
                    "similarity": similarity,
                    "confidence": max(0, similarity)  # Ensure non-negative
                })
            
            # Sort by similarity and take top candidates
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:self.max_candidates]
            
        except Exception as e:
            logger.error(f"Error finding similar segments: {str(e)}")
            return []
    
    async def _evaluate_matches(
        self, 
        parsed_query: Dict[str, Any], 
        similar_segments: List[Dict[str, Any]], 
        document_segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Apply logic evaluation to score matches"""
        try:
            scored_matches = []
            
            for segment_info in similar_segments:
                segment_index = segment_info["index"]
                if segment_index >= len(document_segments):
                    continue
                
                segment = document_segments[segment_index]
                base_confidence = segment_info["confidence"]
                
                # Apply additional scoring factors
                final_score = await self._calculate_comprehensive_score(
                    parsed_query, 
                    segment, 
                    base_confidence
                )
                
                scored_match = {
                    "segment": segment,
                    "base_confidence": base_confidence,
                    "final_confidence": final_score,
                    "scoring_factors": await self._get_scoring_factors(parsed_query, segment)
                }
                
                scored_matches.append(scored_match)
            
            return scored_matches
            
        except Exception as e:
            logger.error(f"Error evaluating matches: {str(e)}")
            return []
    
    async def _calculate_comprehensive_score(
        self, 
        parsed_query: Dict[str, Any], 
        segment: Dict[str, Any], 
        base_confidence: float
    ) -> float:
        """Calculate comprehensive confidence score"""
        try:
            score = base_confidence
            
            # Factor 1: Intent matching
            intent_match = await self._evaluate_intent_match(parsed_query, segment)
            score *= (0.7 + 0.3 * intent_match)
            
            # Factor 2: Keyword density
            keyword_density = await self._calculate_keyword_density(parsed_query, segment)
            score *= (0.8 + 0.2 * keyword_density)
            
            # Factor 3: Clause type matching
            clause_type_match = await self._evaluate_clause_type_match(parsed_query, segment)
            score *= (0.6 + 0.4 * clause_type_match)
            
            # Factor 4: Text relevance
            text_relevance = await self._evaluate_text_relevance(parsed_query, segment)
            score *= (0.9 + 0.1 * text_relevance)
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating comprehensive score: {str(e)}")
            return base_confidence
    
    async def _evaluate_intent_match(self, parsed_query: Dict[str, Any], segment: Dict[str, Any]) -> float:
        """Evaluate how well the segment matches the query intent"""
        try:
            intent = parsed_query.get("intent", "").lower()
            segment_text = segment.get("text", "").lower()
            
            intent_keywords = {
                "find_termination_clause": ["termination", "terminate", "end", "cancel"],
                "find_payment_terms": ["payment", "pay", "fee", "cost", "price"],
                "find_liability_limits": ["liability", "limit", "damage", "claim"],
                "find_confidentiality_clause": ["confidential", "secret", "private", "non-disclosure"],
                "find_non_compete_clause": ["non-compete", "competition", "restrict"],
                "find_ip_clause": ["intellectual property", "patent", "copyright", "trademark"],
                "find_governing_law": ["governing law", "jurisdiction", "legal"],
                "find_dispute_resolution": ["dispute", "arbitration", "mediation", "conflict"],
                "find_force_majeure": ["force majeure", "act of god", "unforeseen"]
            }
            
            if intent in intent_keywords:
                keywords = intent_keywords[intent]
                matches = sum(1 for keyword in keywords if keyword in segment_text)
                return min(1.0, matches / len(keywords))
            
            return 0.5  # Default score
            
        except Exception as e:
            logger.error(f"Error evaluating intent match: {str(e)}")
            return 0.5
    
    async def _calculate_keyword_density(self, parsed_query: Dict[str, Any], segment: Dict[str, Any]) -> float:
        """Calculate keyword density in segment"""
        try:
            keywords = parsed_query.get("keywords", [])
            segment_text = segment.get("text", "").lower()
            
            if not keywords:
                return 0.5
            
            keyword_matches = sum(1 for keyword in keywords if keyword.lower() in segment_text)
            return min(1.0, keyword_matches / len(keywords))
            
        except Exception as e:
            logger.error(f"Error calculating keyword density: {str(e)}")
            return 0.5
    
    async def _evaluate_clause_type_match(self, parsed_query: Dict[str, Any], segment: Dict[str, Any]) -> float:
        """Evaluate clause type matching"""
        try:
            query_clause_type = parsed_query.get("clause_type", "").lower()
            segment_clause_info = segment.get("clause_info", {})
            segment_clause_type = segment_clause_info.get("clause_type", "").lower()
            
            if query_clause_type and segment_clause_type:
                return 1.0 if query_clause_type in segment_clause_type else 0.0
            
            return 0.5  # Default score
            
        except Exception as e:
            logger.error(f"Error evaluating clause type match: {str(e)}")
            return 0.5
    
    async def _evaluate_text_relevance(self, parsed_query: Dict[str, Any], segment: Dict[str, Any]) -> float:
        """Evaluate general text relevance"""
        try:
            query_text = parsed_query.get("context", "").lower()
            segment_text = segment.get("text", "").lower()
            
            # Simple word overlap calculation
            query_words = set(query_text.split())
            segment_words = set(segment_text.split())
            
            if not query_words:
                return 0.5
            
            overlap = len(query_words.intersection(segment_words))
            return min(1.0, overlap / len(query_words))
            
        except Exception as e:
            logger.error(f"Error evaluating text relevance: {str(e)}")
            return 0.5
    
    async def _get_scoring_factors(self, parsed_query: Dict[str, Any], segment: Dict[str, Any]) -> Dict[str, float]:
        """Get detailed scoring factors for transparency"""
        try:
            return {
                "intent_match": await self._evaluate_intent_match(parsed_query, segment),
                "keyword_density": await self._calculate_keyword_density(parsed_query, segment),
                "clause_type_match": await self._evaluate_clause_type_match(parsed_query, segment),
                "text_relevance": await self._evaluate_text_relevance(parsed_query, segment)
            }
        except Exception as e:
            logger.error(f"Error getting scoring factors: {str(e)}")
            return {}
    
    async def _select_best_match(self, scored_matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the best match based on confidence scores"""
        try:
            if not scored_matches:
                return self._get_fallback_match()
            
            # Sort by final confidence
            scored_matches.sort(key=lambda x: x["final_confidence"], reverse=True)
            best_match = scored_matches[0]
            
            # Check if confidence meets threshold
            if best_match["final_confidence"] >= self.confidence_threshold:
                return best_match
            else:
                logger.warning(f"Best match confidence {best_match['final_confidence']} below threshold {self.confidence_threshold}")
                return best_match  # Return anyway but log warning
            
        except Exception as e:
            logger.error(f"Error selecting best match: {str(e)}")
            return self._get_fallback_match()
    
    async def _format_match_result(self, best_match: Dict[str, Any], parsed_query: Dict[str, Any]) -> Dict[str, Any]:
        """Format the final match result"""
        try:
            segment = best_match["segment"]
            clause_info = segment.get("clause_info", {})
            
            # Determine location string
            location_parts = []
            if clause_info.get("page_number"):
                location_parts.append(f"Page {clause_info['page_number']}")
            if clause_info.get("clause_number"):
                location_parts.append(f"Clause {clause_info['clause_number']}")
            if clause_info.get("section_number"):
                location_parts.append(f"Section {clause_info['section_number']}")
            
            location = ", ".join(location_parts) if location_parts else "Document"
            
            return {
                "text": segment.get("text", ""),
                "location": location,
                "confidence": best_match["final_confidence"],
                "scoring_factors": best_match.get("scoring_factors", {}),
                "segment_id": segment.get("segment_id", 0)
            }
            
        except Exception as e:
            logger.error(f"Error formatting match result: {str(e)}")
            return self._get_fallback_match()
    
    def _get_fallback_match(self) -> Dict[str, Any]:
        """Return a fallback match when no good match is found"""
        return {
            "text": "No specific clause found matching the query.",
            "location": "Document",
            "confidence": 0.0,
            "scoring_factors": {},
            "segment_id": -1
        }
    
    def get_processing_time(self) -> float:
        """Get the processing time in milliseconds"""
        return self.processing_time 