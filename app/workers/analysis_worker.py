import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.review import Review, ReviewAnalysis, ProcessingJob

logger = logging.getLogger(__name__)

# Database setup for worker (sync version for RQ)
sync_engine = create_engine(settings.DATABASE_URL)
SyncSessionLocal = sessionmaker(bind=sync_engine)

def process_review(review_id: str):
    """
    Process a single review.
    For Week 1, this is a mock implementation that simulates AI analysis.
    """
    logger.info(f"Processing review: {review_id}")
    
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
        
        # 3. Simulate AI analysis (Week 1: mock analysis)
        analysis_result = mock_analyze_review(review.review_text)
        
        # 4. Save analysis results
        analysis = ReviewAnalysis(
            review_id=review_id,
            sentiment=analysis_result.get("sentiment"),
            urgency=analysis_result.get("urgency"),
            summary=analysis_result.get("summary"),
            topics=analysis_result.get("topics", []),
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

def mock_analyze_review(review_text: str) -> dict:
    """
    Mock AI analysis for Week 1.
    Returns simulated analysis results.
    """
    text_lower = review_text.lower()
    
    # Sentiment detection (very basic)
    positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'best', 'perfect', 'recommend']
    negative_words = ['bad', 'poor', 'terrible', 'awful', 'worst', 'hate', 'disappointed', 'broken']
    
    positive_score = sum(1 for word in positive_words if word in text_lower)
    negative_score = sum(1 for word in negative_words if word in text_lower)
    
    if positive_score > negative_score:
        sentiment = "positive"
    elif negative_score > positive_score:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    # Topic detection (basic)
    topics = []
    topic_keywords = {
        'shipping': ['shipping', 'delivery', 'arrive', 'ship', 'courier', 'fedex', 'ups'],
        'quality': ['quality', 'durable', 'sturdy', 'well-made', 'material'],
        'pricing': ['price', 'cost', 'expensive', 'cheap', 'value', 'money'],
        'customer_service': ['support', 'help', 'service', 'representative', 'agent'],
        'returns': ['return', 'refund', 'exchange', 'money back'],
        'packaging': ['packaging', 'box', 'wrap', 'bubble', 'package'],
    }
    
    for topic, keywords in topic_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            topics.append(topic)
    
    # Urgency detection (basic)
    urgency = "low"
    high_urgency = ['urgent', 'immediately', 'asap', 'emergency', 'critical']
    medium_urgency = ['soon', 'quickly', 'as soon']
    
    if any(word in text_lower for word in high_urgency):
        urgency = "high"
    elif any(word in text_lower for word in medium_urgency):
        urgency = "medium"
    
    # Generate summary
    if topics:
        summary = f"Customer mentioned: {', '.join(topics)}. Overall sentiment: {sentiment}."
    else:
        summary = f"Customer provided feedback. Overall sentiment: {sentiment}."
    
    return {
        "sentiment": sentiment,
        "urgency": urgency,
        "topics": topics[:3],
        "summary": summary[:200],
        "confidence": 0.85
    }