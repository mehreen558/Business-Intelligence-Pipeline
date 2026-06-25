import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from collections import Counter, defaultdict

from app.models.review import Review, ReviewAnalysis

logger = logging.getLogger(__name__)

class TrendService:
    """Service for analyzing trends in review data"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_sentiment_trend(
        self,
        days: int = 30,
        interval: str = 'day'
    ) -> Dict[str, Any]:
        """
        Get sentiment trends over time
        
        Args:
            days: Number of days to analyze
            interval: 'day', 'week', 'month'
        """
        start_date = datetime.now() - timedelta(days=days)
        
        # Query reviews with analysis
        query = select(
            func.date_trunc(interval, Review.created_at).label('period'),
            ReviewAnalysis.sentiment,
            func.count(Review.id).label('count')
        ).join(
            ReviewAnalysis, Review.id == ReviewAnalysis.review_id
        ).where(
            Review.created_at >= start_date
        ).group_by(
            'period',
            ReviewAnalysis.sentiment
        ).order_by('period')
        
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        # Format results
        trend_data = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0, 'mixed': 0})
        periods = []
        
        for row in rows:
            period = row.period.strftime('%Y-%m-%d')
            sentiment = row.sentiment or 'neutral'
            count = row.count
            trend_data[period][sentiment] = count
            if period not in periods:
                periods.append(period)
        
        # Calculate percentages
        sentiment_trend = []
        for period in periods:
            data = trend_data[period]
            total = sum(data.values())
            if total > 0:
                sentiment_trend.append({
                    'period': period,
                    'positive': round((data['positive'] / total) * 100, 1),
                    'negative': round((data['negative'] / total) * 100, 1),
                    'neutral': round((data['neutral'] / total) * 100, 1),
                    'mixed': round((data['mixed'] / total) * 100, 1),
                    'total': total
                })
            else:
                sentiment_trend.append({
                    'period': period,
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0,
                    'mixed': 0,
                    'total': 0
                })
        
        return {
            'periods': periods,
            'data': sentiment_trend,
            'total_reviews': sum(sum(data.values()) for data in trend_data.values())
        }
    
    async def get_topic_trends(
        self,
        days: int = 30,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Get trending topics over time
        """
        start_date = datetime.now() - timedelta(days=days)
        
        # Get all topics from recent reviews
        query = select(
            Review.created_at,
            ReviewAnalysis.topics
        ).join(
            ReviewAnalysis, Review.id == ReviewAnalysis.review_id
        ).where(
            Review.created_at >= start_date
        ).order_by(Review.created_at)
        
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        # Count topics over time
        topic_counts = Counter()
        topic_timeline = defaultdict(lambda: defaultdict(int))
        
        for row in rows:
            created_at = row.created_at
            topics = row.topics or []
            
            for topic in topics:
                topic_counts[topic] += 1
                week_key = created_at.strftime('%Y-%W')
                topic_timeline[week_key][topic] += 1
        
        # Get top topics
        top_topics = [topic for topic, _ in topic_counts.most_common(top_n)]
        
        # Format timeline data
        timeline = []
        for week, topics in sorted(topic_timeline.items()):
            timeline.append({
                'week': week,
                'topics': {topic: topics.get(topic, 0) for topic in top_topics}
            })
        
        return {
            'top_topics': top_topics,
            'topic_counts': dict(topic_counts.most_common(top_n)),
            'timeline': timeline
        }
    
    async def detect_anomalies(
        self,
        days: int = 30,
        threshold: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in review patterns
        
        Args:
            days: Number of days to analyze
            threshold: Standard deviation threshold for anomaly detection
        """
        start_date = datetime.now() - timedelta(days=days)
        
        # Get daily review counts
        query = select(
            func.date_trunc('day', Review.created_at).label('day'),
            func.count(Review.id).label('count')
        ).where(
            Review.created_at >= start_date
        ).group_by('day').order_by('day')
        
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        if len(rows) < 7:
            return [{'message': 'Not enough data for anomaly detection'}]
        
        # Calculate statistics
        counts = [row.count for row in rows]
        mean = sum(counts) / len(counts)
        std = (sum((c - mean) ** 2 for c in counts) / len(counts)) ** 0.5
        
        # Detect anomalies
        anomalies = []
        for row in rows:
            z_score = (row.count - mean) / std if std > 0 else 0
            
            if abs(z_score) > threshold:
                anomalies.append({
                    'date': row.day.strftime('%Y-%m-%d'),
                    'review_count': row.count,
                    'z_score': round(z_score, 2),
                    'deviation': 'above' if z_score > 0 else 'below',
                    'expected': round(mean),
                    'severity': 'high' if abs(z_score) > 3 else 'medium'
                })
        
        return anomalies
    
    async def get_emerging_issues(
        self,
        lookback_days: int = 30,
        compare_days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Identify emerging issues by comparing recent vs historical topics
        """
        # Get current period topics
        current_start = datetime.now() - timedelta(days=compare_days)
        current_topics = await self._get_topics_in_range(current_start, datetime.now())
        
        # Get historical period topics
        historical_start = datetime.now() - timedelta(days=lookback_days + compare_days)
        historical_end = datetime.now() - timedelta(days=compare_days)
        historical_topics = await self._get_topics_in_range(historical_start, historical_end)
        
        # Calculate growth rates
        emerging = []
        all_topics = set(current_topics.keys()) | set(historical_topics.keys())
        
        for topic in all_topics:
            current_count = current_topics.get(topic, 0)
            historical_count = historical_topics.get(topic, 0)
            
            if historical_count == 0 and current_count > 0:
                growth = 100
            elif historical_count == 0 and current_count == 0:
                growth = 0
            else:
                growth = ((current_count - historical_count) / historical_count) * 100
            
            if growth > 50:  # 50% increase threshold
                emerging.append({
                    'topic': topic,
                    'current_count': current_count,
                    'historical_count': historical_count,
                    'growth_percent': round(growth, 1),
                    'severity': 'high' if growth > 200 else 'medium'
                })
        
        return sorted(emerging, key=lambda x: x['growth_percent'], reverse=True)
    
    async def _get_topics_in_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        """Get topic counts within a date range"""
        query = select(
            ReviewAnalysis.topics
        ).join(
            Review, Review.id == ReviewAnalysis.review_id
        ).where(
            and_(
                Review.created_at >= start_date,
                Review.created_at <= end_date
            )
        )
        
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        topic_counts = Counter()
        for row in rows:
            topics = row.topics or []
            for topic in topics:
                topic_counts[topic] += 1
        
        return dict(topic_counts)
    
    async def get_summary_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate a comprehensive summary report
        """
        # Get all metrics
        sentiment_trend = await self.get_sentiment_trend(days)
        topic_trends = await self.get_topic_trends(days)
        anomalies = await self.detect_anomalies(days)
        emerging = await self.get_emerging_issues(days)
        
        # Calculate overall sentiment
        total_sentiments = {}
        for period_data in sentiment_trend['data']:
            for sentiment in ['positive', 'negative', 'neutral', 'mixed']:
                total_sentiments[sentiment] = total_sentiments.get(sentiment, 0) + period_data.get(sentiment, 0)
        
        total_reviews = sum(total_sentiments.values())
        if total_reviews > 0:
            overall_sentiment = {
                'positive': round((total_sentiments.get('positive', 0) / total_reviews) * 100, 1),
                'negative': round((total_sentiments.get('negative', 0) / total_reviews) * 100, 1),
                'neutral': round((total_sentiments.get('neutral', 0) / total_reviews) * 100, 1),
                'mixed': round((total_sentiments.get('mixed', 0) / total_reviews) * 100, 1)
            }
        else:
            overall_sentiment = {'positive': 0, 'negative': 0, 'neutral': 0, 'mixed': 0}
        
        return {
            'period': {
                'days': days,
                'start_date': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                'end_date': datetime.now().strftime('%Y-%m-%d')
            },
            'overall_sentiment': overall_sentiment,
            'sentiment_trend': sentiment_trend['data'],
            'top_topics': topic_trends['top_topics'][:5],
            'topic_counts': topic_trends['topic_counts'],
            'anomalies': anomalies[:5],
            'emerging_issues': emerging[:5],
            'total_reviews': total_reviews,
            'summary': self._generate_summary(overall_sentiment, anomalies, emerging)
        }
    
    def _generate_summary(self, sentiment, anomalies, emerging) -> str:
        """Generate a human-readable summary"""
        summary_parts = []
        
        # Sentiment summary
        if sentiment['positive'] > 70:
            summary_parts.append("Customer sentiment is overwhelmingly positive")
        elif sentiment['positive'] > 50:
            summary_parts.append("Customer sentiment is generally positive")
        elif sentiment['negative'] > 50:
            summary_parts.append("Customer sentiment is concerningly negative")
        else:
            summary_parts.append("Customer sentiment is mixed")
        
        # Anomaly summary
        if anomalies:
            summary_parts.append(f"Found {len(anomalies)} anomalies in review patterns")
        
        # Emerging issues summary
        if emerging:
            summary_parts.append(f"Emerging issues detected: {', '.join([e['topic'] for e in emerging[:3]])}")
        
        return ". ".join(summary_parts) + "."