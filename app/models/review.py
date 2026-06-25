from sqlalchemy import Column, String, Integer, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.models import Base

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False)
    external_id = Column(String(255), nullable=True)
    rating = Column(Integer, nullable=True)
    review_text = Column(Text, nullable=False)
    review_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class ReviewAnalysis(Base):
    __tablename__ = "review_analysis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.id"), nullable=False)
    
    sentiment = Column(String(20), nullable=True)
    urgency = Column(String(20), nullable=True)
    summary = Column(Text, nullable=True)
    topics = Column(JSON, nullable=True)
    entities = Column(JSON, nullable=True)  # NEW
    confidence = Column(Float, nullable=True)
    
    processed_at = Column(DateTime, server_default=func.now())


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.id"), nullable=True)
    status = Column(String(20), default="pending")
    attempts = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())