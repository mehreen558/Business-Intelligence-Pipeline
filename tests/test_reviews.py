#!/usr/bin/env python3
"""
Test script for Review Intelligence Platform
Run with: python test_reviews.py
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
COLORS = {
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'BLUE': '\033[94m',
    'RESET': '\033[0m'
}


def print_header(text):
    """Print a colored header"""
    print(f"\n{COLORS['BLUE']}{'='*60}{COLORS['RESET']}")
    print(f"{COLORS['GREEN']}{text}{COLORS['RESET']}")
    print(f"{COLORS['BLUE']}{'='*60}{COLORS['RESET']}")


def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{COLORS['YELLOW']}{title}:{COLORS['RESET']}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)


def test_health():
    """Test health check endpoint"""
    print_header("1. Health Check")
    response = requests.get("http://localhost:8000/health")
    print_response("Health Status", response)
    return response.status_code == 200


def test_submit_review(review_text, rating, source="shopify"):
    """Submit a test review"""
    payload = {
        "source": source,
        "rating": rating,
        "review_text": review_text
    }
    
    response = requests.post(
        f"{BASE_URL}/reviews/",
        json=payload
    )
    
    if response.status_code == 202:
        data = response.json()
        print(f"[OK] Review submitted: {data['id']}")
        print(f"     Status: {data['status']}")
        print(f"     Queue Position: {data.get('queue_position', 'N/A')}")
        return data['id']
    else:
        print(f"[FAIL] Failed to submit review: {response.status_code}")
        print(response.text)
        return None


def test_get_reviews():
    """Get all reviews"""
    print_header("4. All Reviews")
    response = requests.get(f"{BASE_URL}/reviews/")
    print_response("Reviews", response)
    return response.json()


def test_get_review(review_id):
    """Get a specific review"""
    print_header(f"5. Review Details: {review_id}")
    response = requests.get(f"{BASE_URL}/reviews/{review_id}")
    print_response("Review", response)
    return response.json()


def test_review_status(review_id):
    """Check review processing status"""
    print_header(f"6. Review Status: {review_id}")
    response = requests.get(f"{BASE_URL}/reviews/{review_id}/status")
    print_response("Status", response)
    return response.json()


def test_stats():
    """Get summary statistics"""
    print_header("7. Summary Statistics")
    response = requests.get(f"{BASE_URL}/reviews/stats/summary")
    print_response("Stats", response)
    return response.json()


def test_filter_by_sentiment(sentiment):
    """Filter reviews by sentiment"""
    print_header(f"8. Reviews with sentiment: {sentiment}")
    response = requests.get(f"{BASE_URL}/reviews/?sentiment={sentiment}")
    print_response(f"{sentiment.capitalize()} Reviews", response)
    return response.json()


def test_filter_by_source(source):
    """Filter reviews by source"""
    print_header(f"9. Reviews from source: {source}")
    response = requests.get(f"{BASE_URL}/reviews/?source={source}")
    print_response(f"{source.capitalize()} Reviews", response)
    return response.json()


def wait_for_processing(review_id, max_wait=10):
    """Wait for a review to be processed"""
    print_header("Waiting for processing...")
    
    for i in range(max_wait):
        time.sleep(1)
        response = requests.get(f"{BASE_URL}/reviews/{review_id}")
        data = response.json()
        
        if data.get('analysis') and data['analysis'].get('sentiment'):
            print(f"[OK] Review processed after {i+1} seconds")
            return True
        print(f"     Waiting... ({i+1}s)")
    
    print("[WARN] Timeout waiting for processing")
    return False


def main():
    """Main test sequence"""
    print(f"\n{COLORS['GREEN']}")
    print("+----------------------------------------------------+")
    print("|  Review Intelligence Platform - Test Suite         |")
    print("+----------------------------------------------------+")
    print(f"{COLORS['RESET']}")
    
    # 1. Health Check
    if not test_health():
        print("[FAIL] API not healthy! Make sure the app is running.")
        return
    
    # 2. Submit test reviews
    print_header("2. Submitting Test Reviews")
    
    # Positive review
    review1_id = test_submit_review(
        "Absolutely love this product! Fast shipping and excellent quality. Customer service was very helpful.",
        rating=5
    )
    
    # Negative review
    review2_id = test_submit_review(
        "Terrible quality. Product broke after 2 days. Customer service was useless and rude.",
        rating=1,
        source="amazon"
    )
    
    # Mixed review
    review3_id = test_submit_review(
        "Product works well but shipping took 3 weeks. Also packaging was damaged.",
        rating=3
    )
    
    # Urgent review
    review4_id = test_submit_review(
        "URGENT! The product is defective and dangerous. Need a refund immediately.",
        rating=2,
        source="amazon"
    )
    
    # 3. Wait for processing
    print_header("3. Processing Reviews")
    print("Waiting for AI to analyze reviews...")
    time.sleep(8)  # Give the worker time to process
    
    # 4. Get all reviews
    reviews = test_get_reviews()
    print(f"\n[INFO] Total reviews: {len(reviews)}")
    
    # 5. Get first review details
    if review1_id:
        test_get_review(review1_id)
        test_review_status(review1_id)
    
    # 6. Get statistics
    stats = test_stats()
    print(f"\n[INFO] Statistics:")
    print(f"     Total Reviews: {stats.get('total_reviews', 0)}")
    print(f"     Processed: {stats.get('processed', 0)}")
    print(f"     Pending: {stats.get('pending', 0)}")
    print(f"     Sentiment: {stats.get('sentiment_counts', {})}")
    
    # 7. Filter by sentiment
    test_filter_by_sentiment("positive")
    test_filter_by_sentiment("negative")
    
    # 8. Filter by source
    test_filter_by_source("shopify")
    test_filter_by_source("amazon")
    
    # 9. Summary
    print_header("Test Summary")
    print(f"{COLORS['GREEN']}")
    print("   [OK] All tests completed")
    print(f"   [INFO] Submitted 4 test reviews")
    print(f"   [INFO] Check the API docs at: http://localhost:8000/docs")
    print(f"   [INFO] View stats at: {BASE_URL}/reviews/stats/summary")
    print(f"{COLORS['RESET']}")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print(f"{COLORS['RED']}[ERROR] Cannot connect to API!{COLORS['RESET']}")
        print("Make sure the application is running:")
        print("  docker compose up -d")
        print("  or")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    except KeyboardInterrupt:
        print(f"\n{COLORS['YELLOW']}[WARN] Test interrupted by user{COLORS['RESET']}")
    except Exception as e:
        print(f"{COLORS['RED']}[ERROR] Unexpected error: {e}{COLORS['RESET']}")