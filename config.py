import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "500"))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    
    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
    
    # Database Configuration
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost/hackrx_db"
    )
    
    # Authentication
    AUTH_TOKEN = os.getenv(
        "AUTH_TOKEN", 
        "15d8d43a4a6736a9d7c238f8fd1b44c29eaac0098c94a7c6ad802075b77bd355"
    )
    
    # Processing Configuration
    SEGMENT_SIZE = int(os.getenv("SEGMENT_SIZE", "1000"))
    SEGMENT_OVERLAP = int(os.getenv("SEGMENT_OVERLAP", "200"))
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
    MAX_CANDIDATES = int(os.getenv("MAX_CANDIDATES", "10"))
    
    # Performance Configuration
    PROCESSING_TIMEOUT = int(os.getenv("PROCESSING_TIMEOUT", "30"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # Webhook Configuration
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_ENABLED = os.getenv("WEBHOOK_ENABLED", "false").lower() == "true"
    WEBHOOK_TIMEOUT = int(os.getenv("WEBHOOK_TIMEOUT", "30"))
    
    @classmethod
    def get_all_config(cls) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return {
            "openai_api_key": cls.OPENAI_API_KEY,
            "llm_model": cls.LLM_MODEL,
            "llm_max_tokens": cls.LLM_MAX_TOKENS,
            "llm_temperature": cls.LLM_TEMPERATURE,
            "embedding_model": cls.EMBEDDING_MODEL,
            "embedding_dimension": cls.EMBEDDING_DIMENSION,
            "database_url": cls.DATABASE_URL,
            "auth_token": cls.AUTH_TOKEN,
            "segment_size": cls.SEGMENT_SIZE,
            "segment_overlap": cls.SEGMENT_OVERLAP,
            "confidence_threshold": cls.CONFIDENCE_THRESHOLD,
            "max_candidates": cls.MAX_CANDIDATES,
            "processing_timeout": cls.PROCESSING_TIMEOUT,
            "batch_size": cls.BATCH_SIZE,
            "log_level": cls.LOG_LEVEL,
            "environment": cls.ENVIRONMENT,
            "webhook_url": cls.WEBHOOK_URL,
            "webhook_enabled": cls.WEBHOOK_ENABLED,
            "webhook_timeout": cls.WEBHOOK_TIMEOUT
        }
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production"""
        return cls.ENVIRONMENT.lower() == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development"""
        return cls.ENVIRONMENT.lower() == "development" 