from fastapi import APIRouter, HTTPException, Depends # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.models.review import Review, ReviewAnalysis, ProcessingJob
from app.core.queue import get_analysis_queue

router = APIRouter()

# ----- Request/Response Models -----
class ReviewIngestRequest(BaseModel):
    source: str = Field(..., description="Source of review (shopify, amazon, etc.)")
    external_id: Optional[str] = Field(None, description="ID from source system")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating 1-5")
    review_text: str = Field(..., min_length=1, description="Review content")
    review_date: Optional[datetime] = Field(None, description="Date of review")

class ReviewIngestResponse(BaseModel):
    id: uuid.UUID
    status: str
    message: str
    queue_position: Optional[int] = None

class AnalysisResponse(BaseModel):
    id: uuid.UUID
    sentiment: Optional[str]
    urgency: Optional[str]
    summary: Optional[str]
    topics: List[str] = []
    confidence: Optional[float]
    processed_at: Optional[datetime]

class ReviewResponse(BaseModel):
    id: uuid.UUID
    source: str
    external_id: Optional[str]
    rating: Optional[int]
    review_text: str
    review_date: Optional[datetime]
    created_at: datetime
    analysis: Optional[AnalysisResponse]

class JobStatusResponse(BaseModel):
    review_id: uuid.UUID
    status: str
    attempts: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

# ----- Endpoints -----

@router.post("/", response_model=ReviewIngestResponse, status_code=202)
async def ingest_review(
    request: ReviewIngestRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest a new review for analysis.
    """
    # 1. Create review record
    review = Review(
        id=str(uuid.uuid4()),
        source=request.source,
        external_id=request.external_id,
        rating=request.rating,
        review_text=request.review_text,
        review_date=request.review_date or datetime.now()
    )
    
    db.add(review)
    await db.commit()
    await db.refresh(review)
    
    # 2. Create job tracking record
    processing_job = ProcessingJob(
        id=str(uuid.uuid4()),
        review_id=review.id,
        status="pending",
        attempts=0
    )
    db.add(processing_job)
    await db.commit()
    
    # 3. Queue for analysis
    queue = get_analysis_queue()
    from app.workers.analysis_worker import process_review
    
    job = queue.enqueue(
        process_review,
        str(review.id),
        job_timeout=300,
        result_ttl=86400
    )
    
    queue_length = len(queue)
    
    return ReviewIngestResponse(
        id=review.id,
        status="queued",
        message="Review received and queued for processing",
        queue_position=queue_length
    )

@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a review and its analysis if available.
    """
    review = await db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    analysis_result = await db.execute(select(ReviewAnalysis).where(ReviewAnalysis.review_id == review_id))
    analysis = analysis_result.scalars().first()
    
    response = ReviewResponse(
        id=review.id,
        source=review.source,
        external_id=review.external_id,
        rating=review.rating,
        review_text=review.review_text,
        review_date=review.review_date,
        created_at=review.created_at,
        analysis=None
    )
    
    if analysis:
        response.analysis = AnalysisResponse(
            id=analysis.id,
            sentiment=analysis.sentiment,
            urgency=analysis.urgency,
            summary=analysis.summary,
            topics=analysis.topics or [],
            confidence=analysis.confidence,
            processed_at=analysis.processed_at
        )
    
    return response

@router.get("/{review_id}/status", response_model=JobStatusResponse)
async def get_job_status(
    review_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the processing status of a review.
    """
    result = await db.execute(select(ProcessingJob).where(ProcessingJob.review_id == review_id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(
        review_id=job.review_id,
        status=job.status,
        attempts=job.attempts,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at
    )

@router.get("/", response_model=List[ReviewResponse])
async def list_reviews(
    limit: int = 10,
    offset: int = 0,
    source: Optional[str] = None,
    sentiment: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List reviews with optional filtering.
    """
    query = select(Review)
    
    if source:
        query = query.where(Review.source == source)
    
    if sentiment:
        query = query.join(ReviewAnalysis).where(ReviewAnalysis.sentiment == sentiment)
    
    query = query.order_by(Review.created_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    review_responses = []
    for review in reviews:
        analysis_result = await db.execute(select(ReviewAnalysis).where(ReviewAnalysis.review_id == review.id))
        analysis = analysis_result.scalars().first()
        
        review_response = ReviewResponse(
            id=review.id,
            source=review.source,
            external_id=review.external_id,
            rating=review.rating,
            review_text=review.review_text,
            review_date=review.review_date,
            created_at=review.created_at,
            analysis=None
        )
        
        if analysis:
            review_response.analysis = AnalysisResponse(
                id=analysis.id,
                sentiment=analysis.sentiment,
                urgency=analysis.urgency,
                summary=analysis.summary,
                topics=analysis.topics or [],
                confidence=analysis.confidence,
                processed_at=analysis.processed_at
            )
        
        review_responses.append(review_response)
    
    return review_responses

@router.get("/stats/summary")
async def get_summary_stats(db: AsyncSession = Depends(get_db)):
    """
    Get basic statistics about reviews.
    """
    # Total reviews
    total_reviews = await db.execute(select(func.count(Review.id)))
    total_reviews = total_reviews.scalar() or 0
    
    # Sentiment breakdown
    sentiment_counts = {}
    sentiments = await db.execute(
        select(ReviewAnalysis.sentiment, func.count(ReviewAnalysis.id))
        .group_by(ReviewAnalysis.sentiment)
    )
    
    for sentiment, count in sentiments:
        sentiment_counts[sentiment] = count
    
    # Recent reviews (last 24 hours)
    yesterday = datetime.now() - timedelta(days=1)
    recent_reviews = await db.execute(
        select(func.count(Review.id))
        .where(Review.created_at >= yesterday)
    )
    recent_reviews = recent_reviews.scalar() or 0
    
    # Count processed reviews
    processed = await db.execute(select(func.count(ReviewAnalysis.id)))
    processed = processed.scalar() or 0
    
    return {
        "total_reviews": total_reviews,
        "sentiment_counts": sentiment_counts,
        "recent_24h": recent_reviews,
        "processed": processed,
        "pending": total_reviews - processed
    }