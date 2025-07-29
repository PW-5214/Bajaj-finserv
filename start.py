#!/usr/bin/env python3
"""
Startup script for the LLM-Powered Query Retrieval System
"""

import uvicorn
import logging
import sys
import os
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

def check_environment():
    """Check if the environment is properly configured"""
    logger.info("🔍 Checking environment configuration...")
    
    # Check OpenAI API key
    if Config.OPENAI_API_KEY == "your-openai-api-key":
        logger.warning("⚠️  OpenAI API key not configured. Some features may not work.")
        logger.info("💡 Set OPENAI_API_KEY environment variable for full functionality.")
    else:
        logger.info("✅ OpenAI API key configured")
    
    # Check database configuration
    if "localhost" in Config.DATABASE_URL:
        logger.info("ℹ️  Using local database configuration")
    else:
        logger.info("✅ Database URL configured")
    
    # Check authentication token
    if Config.AUTH_TOKEN:
        logger.info("✅ Authentication token configured")
    else:
        logger.error("❌ Authentication token not configured")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🚀 LLM-Powered Query Retrieval System")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed. Please configure required settings.")
        sys.exit(1)
    
    # Display configuration
    print("\n📋 Configuration:")
    print(f"Environment: {Config.ENVIRONMENT}")
    print(f"Log Level: {Config.LOG_LEVEL}")
    print(f"Database: {Config.DATABASE_URL.split('@')[-1] if '@' in Config.DATABASE_URL else 'SQLite'}")
    print(f"LLM Model: {Config.LLM_MODEL}")
    print(f"Embedding Model: {Config.EMBEDDING_MODEL}")
    
    # Start the server
    print(f"\n🌐 Starting server on http://localhost:8000")
    print("📖 API documentation available at http://localhost:8000/docs")
    print("🔧 Health check available at http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=Config.is_development(),
            log_level=Config.LOG_LEVEL.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 