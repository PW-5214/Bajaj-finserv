import os
import asyncio
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
import json
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

Base = declarative_base()

class DocumentInteraction(Base):
    """Database model for document interactions"""
    __tablename__ = "document_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_url = Column(String(500), nullable=False)
    user_query = Column(Text, nullable=False)
    matched_clause = Column(JSON, nullable=True)
    confidence = Column(Float, default=0.0)
    processing_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True)

class DatabaseService:
    """Handles database operations for the query retrieval system"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.database_url = os.getenv(
            "DATABASE_URL", 
            "postgresql://user:password@localhost/hackrx_db"
        )
    
    async def initialize(self):
        """Initialize database connection and create tables"""
        try:
            # Create engine
            self.engine = create_engine(
                self.database_url,
                poolclass=StaticPool,
                echo=False
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.warning(f"Database initialization failed, using in-memory storage: {e}")
            # Fallback to in-memory storage
            self.engine = create_engine(
                "sqlite:///:memory:",
                poolclass=StaticPool,
                echo=False
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            Base.metadata.create_all(bind=self.engine)
            logger.info("Using in-memory SQLite database")
    
    async def log_interaction(
        self, 
        document_url: str, 
        user_query: str, 
        matched_clause: Dict[str, Any], 
        confidence: float,
        processing_time_ms: float = 0.0,
        metadata: Dict[str, Any] = None
    ):
        """Log a document interaction"""
        try:
            db = self.SessionLocal()
            
            interaction = DocumentInteraction(
                document_url=document_url,
                user_query=user_query,
                matched_clause=matched_clause,
                confidence=confidence,
                processing_time_ms=processing_time_ms,
                metadata=metadata or {}
            )
            
            db.add(interaction)
            db.commit()
            db.close()
            
            logger.info(f"Interaction logged for document: {document_url}")
            
        except Exception as e:
            logger.error(f"Error logging interaction: {str(e)}")
            if db:
                db.rollback()
                db.close()
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            db = self.SessionLocal()
            
            # Total queries
            total_queries = db.query(DocumentInteraction).count()
            
            # Average confidence
            avg_confidence = db.query(DocumentInteraction.confidence).filter(
                DocumentInteraction.confidence > 0
            ).all()
            avg_confidence = sum([c[0] for c in avg_confidence]) / len(avg_confidence) if avg_confidence else 0.0
            
            # Most common queries (simplified)
            recent_queries = db.query(DocumentInteraction.user_query).order_by(
                DocumentInteraction.created_at.desc()
            ).limit(10).all()
            
            most_common_queries = [q[0] for q in recent_queries]
            
            db.close()
            
            return {
                "total_queries": total_queries,
                "average_confidence": round(avg_confidence, 3),
                "most_common_queries": most_common_queries
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {
                "total_queries": 0,
                "average_confidence": 0.0,
                "most_common_queries": []
            }
    
    async def get_recent_interactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent document interactions"""
        try:
            db = self.SessionLocal()
            
            interactions = db.query(DocumentInteraction).order_by(
                DocumentInteraction.created_at.desc()
            ).limit(limit).all()
            
            result = []
            for interaction in interactions:
                result.append({
                    "id": interaction.id,
                    "document_url": interaction.document_url,
                    "user_query": interaction.user_query,
                    "confidence": interaction.confidence,
                    "created_at": interaction.created_at.isoformat(),
                    "processing_time_ms": interaction.processing_time_ms
                })
            
            db.close()
            return result
            
        except Exception as e:
            logger.error(f"Error getting recent interactions: {str(e)}")
            return []
    
    async def get_document_stats(self, document_url: str) -> Dict[str, Any]:
        """Get statistics for a specific document"""
        try:
            db = self.SessionLocal()
            
            # Count interactions for this document
            total_interactions = db.query(DocumentInteraction).filter(
                DocumentInteraction.document_url == document_url
            ).count()
            
            # Average confidence for this document
            confidences = db.query(DocumentInteraction.confidence).filter(
                DocumentInteraction.document_url == document_url,
                DocumentInteraction.confidence > 0
            ).all()
            
            avg_confidence = sum([c[0] for c in confidences]) / len(confidences) if confidences else 0.0
            
            # Most common queries for this document
            common_queries = db.query(DocumentInteraction.user_query).filter(
                DocumentInteraction.document_url == document_url
            ).limit(5).all()
            
            db.close()
            
            return {
                "document_url": document_url,
                "total_interactions": total_interactions,
                "average_confidence": round(avg_confidence, 3),
                "common_queries": [q[0] for q in common_queries]
            }
            
        except Exception as e:
            logger.error(f"Error getting document stats: {str(e)}")
            return {
                "document_url": document_url,
                "total_interactions": 0,
                "average_confidence": 0.0,
                "common_queries": []
            }
    
    async def cleanup_old_interactions(self, days_old: int = 30):
        """Clean up old interactions"""
        try:
            db = self.SessionLocal()
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            deleted_count = db.query(DocumentInteraction).filter(
                DocumentInteraction.created_at < cutoff_date
            ).delete()
            
            db.commit()
            db.close()
            
            logger.info(f"Cleaned up {deleted_count} old interactions")
            
        except Exception as e:
            logger.error(f"Error cleaning up old interactions: {str(e)}")
            if db:
                db.rollback()
                db.close()
    
    async def close(self):
        """Close database connections"""
        try:
            if self.engine:
                self.engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database: {str(e)}") 