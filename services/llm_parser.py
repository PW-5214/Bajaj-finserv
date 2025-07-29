import openai
import os
from typing import Dict, Any, List
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMParser:
    """Handles LLM-based query parsing and response generation"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
        self.model = "gpt-4"
        self.token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
        
        # Initialize OpenAI client
        openai.api_key = self.api_key
    
    async def parse_query(self, user_query: str) -> Dict[str, Any]:
        """
        Parse user query to extract structured search intent
        """
        try:
            system_prompt = """
            You are an expert legal and business document analyzer. Your task is to parse user queries and extract structured search intent.
            
            Analyze the query and return a JSON object with:
            - intent: The main search intent (e.g., "find_termination_clause", "find_payment_terms", "find_liability_limits")
            - keywords: List of important keywords for semantic search
            - clause_type: Type of clause being sought
            - context: Additional context that might help in matching
            
            Focus on legal, insurance, HR, and compliance domains.
            """
            
            user_prompt = f"Parse this query: '{user_query}'"
            
            response = await self._call_openai(system_prompt, user_prompt)
            
            # Parse the response
            try:
                parsed_result = json.loads(response)
            except json.JSONDecodeError:
                # Fallback parsing if JSON is malformed
                parsed_result = self._fallback_parse(user_query)
            
            logger.info(f"Query parsed successfully: {parsed_result}")
            return parsed_result
            
        except Exception as e:
            logger.error(f"Error parsing query: {str(e)}")
            return self._fallback_parse(user_query)
    
    async def generate_rationale(self, user_query: str, matched_clause: Dict[str, Any], document_content: str) -> str:
        """
        Generate explainable rationale for the matched clause
        """
        try:
            system_prompt = """
            You are an expert legal analyst. Explain why a specific clause matches a user's query.
            Provide clear, concise reasoning that connects the user's question to the matched clause.
            Focus on legal relevance and practical implications.
            """
            
            user_prompt = f"""
            User Query: {user_query}
            
            Matched Clause: {matched_clause.get('text', '')}
            Clause Location: {matched_clause.get('location', '')}
            Confidence Score: {matched_clause.get('confidence', 0.0)}
            
            Explain why this clause is the best match for the user's query.
            """
            
            response = await self._call_openai(system_prompt, user_prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating rationale: {str(e)}")
            return f"Clause matched based on semantic similarity with confidence {matched_clause.get('confidence', 0.0)}"
    
    async def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """
        Make OpenAI API call with token tracking
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # Track token usage
            usage = response.usage
            self.token_usage["prompt_tokens"] += usage.prompt_tokens
            self.token_usage["completion_tokens"] += usage.completion_tokens
            self.token_usage["total_tokens"] += usage.total_tokens
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def _fallback_parse(self, user_query: str) -> Dict[str, Any]:
        """
        Fallback parsing when LLM fails
        """
        # Simple keyword-based parsing
        query_lower = user_query.lower()
        
        intent_mapping = {
            "termination": "find_termination_clause",
            "payment": "find_payment_terms",
            "liability": "find_liability_limits",
            "confidentiality": "find_confidentiality_clause",
            "non-compete": "find_non_compete_clause",
            "intellectual property": "find_ip_clause",
            "governing law": "find_governing_law",
            "dispute": "find_dispute_resolution",
            "force majeure": "find_force_majeure"
        }
        
        intent = "general_search"
        clause_type = None
        
        for keyword, mapped_intent in intent_mapping.items():
            if keyword in query_lower:
                intent = mapped_intent
                clause_type = keyword
                break
        
        return {
            "intent": intent,
            "keywords": user_query.split(),
            "clause_type": clause_type,
            "context": user_query
        }
    
    def get_token_usage(self) -> Dict[str, int]:
        """Get current token usage statistics"""
        return self.token_usage.copy()
    
    def reset_token_usage(self):
        """Reset token usage counters"""
        self.token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        } 