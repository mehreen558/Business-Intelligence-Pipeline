import json
import logging
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """AI service for analyzing reviews using OpenAI"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=settings.OPENAI_API_KEY,
                max_retries=3,
                timeout=30.0
            )
            logger.info("OpenAI client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
            raise
    
    def analyze_review(self, review_text: str) -> Dict[str, Any]:
        """
        Analyze a review using OpenAI
        
        Returns:
            {
                "sentiment": "positive|negative|neutral|mixed",
                "urgency": "low|medium|high",
                "topics": ["topic1", "topic2"],
                "summary": "Brief summary",
                "confidence": 0.95,
                "entities": {"people": [], "companies": [], "products": []}
            }
        """
        try:
            prompt = self._build_prompt(review_text)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Cheaper model for testing
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a customer review analysis expert. Extract insights from reviews and return JSON only. Never include any other text besides the JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500,
                response_format={"type": "json_object"}  # Ensures valid JSON
            )
            
            # Parse the JSON response
            result = json.loads(response.choices[0].message.content)
            
            # Ensure all required fields exist
            required_fields = ["sentiment", "urgency", "topics", "summary", "confidence"]
            for field in required_fields:
                if field not in result:
                    result[field] = None
            
            return result
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._fallback_analysis(review_text, str(e))
    
    def _build_prompt(self, review_text: str) -> str:
        """Build the prompt for OpenAI"""
        return f"""
        Analyze this customer review and return structured insights.
        
        Review: "{review_text}"
        
        Return JSON ONLY with these exact fields:
        {{
            "sentiment": "positive" or "negative" or "neutral" or "mixed",
            "urgency": "low" or "medium" or "high",
            "topics": ["topic1", "topic2", "topic3"],
            "summary": "1-2 sentence summary of what the customer said",
            "confidence": 0.0 to 1.0,
            "entities": {{
                "people": ["list of people mentioned"],
                "companies": ["list of companies mentioned"], 
                "products": ["list of products mentioned"]
            }}
        }}
        
        Topics can include: shipping, pricing, quality, customer_service, returns, website, billing, packaging, delivery, performance, design, features, support, communication, reliability, value, ease_of_use
        
        Confidence should reflect how certain you are about the analysis.
        
        Only respond with valid JSON. No other text.
        """
    
    def _fallback_analysis(self, review_text: str, error: str) -> Dict[str, Any]:
        """Return a fallback analysis when AI fails"""
        text_lower = review_text.lower()
        
        # Simple sentiment detection
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
        
        # Topic detection
        topics = []
        topic_keywords = {
            'shipping': ['shipping', 'delivery', 'arrive', 'ship', 'courier'],
            'quality': ['quality', 'durable', 'sturdy', 'well-made'],
            'pricing': ['price', 'cost', 'expensive', 'cheap', 'value'],
            'customer_service': ['support', 'help', 'service', 'representative'],
            'returns': ['return', 'refund', 'exchange'],
            'packaging': ['packaging', 'box', 'wrap', 'bubble'],
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return {
            "sentiment": sentiment,
            "urgency": "medium",
            "topics": topics[:3] if topics else ["general"],
            "summary": f"Customer provided feedback about {', '.join(topics) if topics else 'product'}.",
            "confidence": 0.5,
            "entities": {"people": [], "companies": [], "products": []},
            "error": error
        }


# Create a singleton instance
ai_service = AIService()

def get_ai_service():
    return ai_service