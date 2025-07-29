import os
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

class AuthService:
    """Handles authentication and authorization"""
    
    def __init__(self):
        # The expected token from the requirements
        self.expected_token = "15d8d43a4a6736a9d7c238f8fd1b44c29eaac0098c94a7c6ad802075b77bd355"
        
        # Token cache for performance
        self.token_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def verify_token(self, token: str) -> bool:
        """
        Verify if the provided token is valid
        """
        try:
            # Check if token is in cache
            if token in self.token_cache:
                cached_result = self.token_cache[token]
                if datetime.utcnow() < cached_result["expires"]:
                    return cached_result["valid"]
                else:
                    # Remove expired cache entry
                    del self.token_cache[token]
            
            # Verify token
            is_valid = self._validate_token(token)
            
            # Cache the result
            self.token_cache[token] = {
                "valid": is_valid,
                "expires": datetime.utcnow() + timedelta(seconds=self.cache_ttl)
            }
            
            if is_valid:
                logger.info("Token verification successful")
            else:
                logger.warning(f"Invalid token provided: {token[:10]}...")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return False
    
    def _validate_token(self, token: str) -> bool:
        """
        Validate the token against expected value
        """
        try:
            # Direct comparison with expected token
            if token == self.expected_token:
                return True
            
            # Additional validation logic can be added here
            # For example, checking token format, expiration, etc.
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return False
    
    def generate_token(self, user_id: str, secret: str = None) -> str:
        """
        Generate a new token (for testing purposes)
        """
        try:
            if secret is None:
                secret = "hackrx_secret_key"
            
            # Create a hash based on user_id and secret
            token_data = f"{user_id}:{secret}:{datetime.utcnow().isoformat()}"
            token_hash = hashlib.sha256(token_data.encode()).hexdigest()
            
            logger.info(f"Generated new token for user: {user_id}")
            return token_hash
            
        except Exception as e:
            logger.error(f"Error generating token: {str(e)}")
            return ""
    
    def get_token_info(self, token: str) -> Dict[str, Any]:
        """
        Get information about a token (for debugging)
        """
        try:
            if token == self.expected_token:
                return {
                    "valid": True,
                    "type": "api_token",
                    "created": "2025-01-01T00:00:00Z",
                    "expires": None
                }
            else:
                return {
                    "valid": False,
                    "error": "Invalid token"
                }
                
        except Exception as e:
            logger.error(f"Error getting token info: {str(e)}")
            return {"valid": False, "error": str(e)}
    
    def cleanup_expired_cache(self):
        """
        Clean up expired cache entries
        """
        try:
            current_time = datetime.utcnow()
            expired_tokens = [
                token for token, cache_data in self.token_cache.items()
                if current_time >= cache_data["expires"]
            ]
            
            for token in expired_tokens:
                del self.token_cache[token]
            
            if expired_tokens:
                logger.info(f"Cleaned up {len(expired_tokens)} expired cache entries")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired cache: {str(e)}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        """
        try:
            return {
                "cache_size": len(self.token_cache),
                "cache_ttl_seconds": self.cache_ttl,
                "expected_token_length": len(self.expected_token)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {} 