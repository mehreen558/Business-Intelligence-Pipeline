import json
from typing import Dict, Any, List
from datetime import datetime

class VisualizationService:
    """Generate data for visualizations"""
    
    @staticmethod
    def format_chart_data(trend_data: List[Dict]) -> Dict[str, Any]:
        """Format trend data for charts"""
        return {
            'labels': [d['period'] for d in trend_data],
            'datasets': [
                {
                    'label': 'Positive',
                    'data': [d['positive'] for d in trend_data],
                    'color': '#4CAF50'
                },
                {
                    'label': 'Negative',
                    'data': [d['negative'] for d in trend_data],
                    'color': '#f44336'
                },
                {
                    'label': 'Neutral',
                    'data': [d['neutral'] for d in trend_data],
                    'color': '#FFC107'
                },
                {
                    'label': 'Mixed',
                    'data': [d['mixed'] for d in trend_data],
                    'color': '#2196F3'
                }
            ]
        }
    
    @staticmethod
    def format_topic_chart(topics: Dict[str, int]) -> Dict[str, Any]:
        """Format topic data for charts"""
        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        return {
            'labels': [t[0] for t in sorted_topics],
            'data': [t[1] for t in sorted_topics]
        }
    
    @staticmethod
    def get_trend_direction(trend_data: List[Dict], metric: str = 'positive') -> str:
        """Determine trend direction"""
        if len(trend_data) < 3:
            return 'insufficient_data'
        
        values = [d[metric] for d in trend_data[-7:]]  # Last 7 days
        if values[-1] > values[0]:
            return 'improving'
        elif values[-1] < values[0]:
            return 'declining'
        else:
            return 'stable'