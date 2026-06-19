from sqlalchemy import Column, String, Integer, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from app.models import Base
import uuid

class Review(Base):
    __tablename__ = "reviews"
    
    # Use String for SQLite compatibility (store UUID as string)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(50), nullable=False)
    external_id = Column(String(255), nullable=True)
    rating = Column(Integer, nullable=True)
    review_text = Column(Text, nullable=False)
    review_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<Review(id={self.id}, source={self.source})>"


class ReviewAnalysis(Base):
    __tablename__ = "review_analysis"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = Column(String(36), ForeignKey("reviews.id"), nullable=False)
    
    sentiment = Column(String(20), nullable=True)
    urgency = Column(String(20), nullable=True)
    summary = Column(Text, nullable=True)
    topics = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=True)
    
    processed_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<ReviewAnalysis(review_id={self.review_id}, sentiment={self.sentiment})>"


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = Column(String(36), ForeignKey("reviews.id"), nullable=True)
    status = Column(String(20), default="pending")
    attempts = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ProcessingJob(id={self.id}, status={self.status})>"