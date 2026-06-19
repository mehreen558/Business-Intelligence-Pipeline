from redis import Redis
from rq import Queue
from app.core.config import settings

# Redis connection
redis_conn = Redis.from_url(settings.REDIS_URL)

# Analysis queue
analysis_queue = Queue('analysis', connection=redis_conn, default_timeout=300)

def get_analysis_queue():
    """Get the analysis queue instance"""
    return analysis_queue

def get_redis_connection():
    """Get Redis connection for direct operations"""
    return redis_conn