import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.review import Review, ReviewAnalysis, ProcessingJob
from app.services.ai_services import get_ai_service

logger = logging.getLogger(__name__)

# Database setup for worker
sync_engine = create_engine(settings.DATABASE_URL)
SyncSessionLocal = sessionmaker(bind=sync_engine)

def process_review(review_id: str):
    """
    Process a review using OpenAI
    """
    logger.info(f" Processing review: {review_id}")
    
    db = SyncSessionLocal()
    
    try:
        # 1. Get the review
        review = db.query(Review).filter_by(id=review_id).first()
        if not review:
            logger.error(f"Review {review_id} not found")
            return
        
        # 2. Get or create job record
        job = db.query(ProcessingJob).filter_by(review_id=review_id).first()
        if not job:
            job = ProcessingJob(review_id=review_id, status="processing")
            db.add(job)
            db.commit()
        else:
            job.status = "processing"
            job.attempts += 1
            db.commit()
        
        # 3. Analyze with OpenAI
        logger.info(f"Sending to OpenAI...")
        ai_service = get_ai_service()
        analysis_result = ai_service.analyze_review(review.review_text)
        
        logger.info(f"AI analysis complete for {review_id}")
        logger.info(f"   Sentiment: {analysis_result.get('sentiment')}")
        logger.info(f"   Topics: {analysis_result.get('topics')}")
        logger.info(f"   Confidence: {analysis_result.get('confidence')}")
        
        # 4. Save analysis results
        analysis = ReviewAnalysis(
            review_id=review_id,
            sentiment=analysis_result.get("sentiment"),
            urgency=analysis_result.get("urgency"),
            summary=analysis_result.get("summary"),
            topics=analysis_result.get("topics", []),
            entities=analysis_result.get("entities", {}),
            confidence=analysis_result.get("confidence", 0.0)
        )
        db.add(analysis)
        
        # 5. Update job status
        job.status = "completed"
        db.commit()
        
        logger.info(f"Successfully processed review {review_id}")
        
    except Exception as e:
        logger.error(f"Error processing review {review_id}: {str(e)}")
        db.rollback()
        
        # Update job with error
        job = db.query(ProcessingJob).filter_by(review_id=review_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.attempts += 1
            db.commit()
        raise
    finally:
        db.close()