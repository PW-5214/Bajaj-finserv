from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
import json
import asyncio
from datetime import datetime
import logging

from services.document_processor import DocumentProcessor
from services.llm_parser import LLMParser
from services.embedding_service import EmbeddingService
from services.clause_matcher import ClauseMatcher
from services.database import DatabaseService
from services.auth_service import AuthService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLM-Powered Query Retrieval System",
    description="Intelligent document query system for insurance, legal, HR, and compliance domains",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
document_processor = DocumentProcessor()
llm_parser = LLMParser()
embedding_service = EmbeddingService()
clause_matcher = ClauseMatcher()
db_service = DatabaseService()
auth_service = AuthService()

class QueryRequest(BaseModel):
    document_url: str
    user_query: str

class QueryResponse(BaseModel):
    query: str
    matched_clause: Dict[str, Any]
    decision_rationale: str
    metadata: Dict[str, Any]

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await db_service.initialize()
    await embedding_service.initialize()
    logger.info("Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await db_service.close()
    await embedding_service.close()
    logger.info("Application shutdown complete")

async def verify_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify authentication token"""
    token = credentials.credentials
    if not auth_service.verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return token

@app.post("/hackrx/run", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    token: str = Depends(verify_auth)
):
    """
    Main endpoint for processing document queries
    """
    try:
        logger.info(f"Processing query: {request.user_query}")
        
        # Step 1: Process document
        document_content = await document_processor.process_document(request.document_url)
        
        # Step 2: Parse query using LLM
        parsed_query = await llm_parser.parse_query(request.user_query)
        
        # Step 3: Generate embeddings for document segments
        document_segments = document_processor.segment_document(document_content)
        embeddings = await embedding_service.generate_embeddings(document_segments)
        
        # Step 4: Match clauses using semantic search
        matched_clause = await clause_matcher.find_best_match(
            parsed_query, 
            document_segments, 
            embeddings
        )
        
        # Step 5: Generate decision rationale
        rationale = await llm_parser.generate_rationale(
            request.user_query, 
            matched_clause, 
            document_content
        )
        
        # Step 6: Log the interaction
        await db_service.log_interaction(
            document_url=request.document_url,
            user_query=request.user_query,
            matched_clause=matched_clause,
            confidence=matched_clause.get("confidence", 0.0)
        )
        
        # Step 7: Prepare response
        response = QueryResponse(
            query=request.user_query,
            matched_clause=matched_clause,
            decision_rationale=rationale,
            metadata={
                "source_document": request.document_url,
                "processed_at": datetime.utcnow().isoformat() + "Z",
                "token_usage": llm_parser.get_token_usage(),
                "processing_time_ms": clause_matcher.get_processing_time()
            }
        )
        
        logger.info(f"Query processed successfully with confidence: {matched_clause.get('confidence', 0.0)}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/stats")
async def get_stats(token: str = Depends(verify_auth)):
    """Get system statistics"""
    stats = await db_service.get_statistics()
    return {
        "total_queries": stats.get("total_queries", 0),
        "average_confidence": stats.get("average_confidence", 0.0),
        "most_common_queries": stats.get("most_common_queries", []),
        "system_uptime": "active"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 