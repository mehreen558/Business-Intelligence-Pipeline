import asyncio
import httpx
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

async def test_ingest_review():
    """Test ingesting a review"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/reviews/",
            json={
                "source": "shopify",
                "rating": 5,
                "review_text": "Absolutely love this product! Would definitely recommend to others.",
                "review_date": "2026-06-15T10:00:00Z"
            }
        )
        result = response.json()
        print(f"Ingest result: {json.dumps(result, indent=2)}")
        return result['id']

async def test_get_review(review_id):
    """Test getting a review"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/reviews/{review_id}")
        result = response.json()
        print(f"Review: {json.dumps(result, indent=2)}")

async def test_get_status(review_id):
    """Test getting job status"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/reviews/{review_id}/status")
        result = response.json()
        print(f"Status: {json.dumps(result, indent=2)}")

async def test_list_reviews():
    """Test listing reviews"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/reviews/?limit=5")
        result = response.json()
        print(f"List: {json.dumps(result, indent=2)}")

async def test_stats():
    """Test getting stats"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/reviews/stats/summary")
        result = response.json()
        print(f"Stats: {json.dumps(result, indent=2)}")

async def main():
    print("=== Testing Week 1 Implementation ===\n")
    
    # Test ingestion
    print("1. Testing ingestion...")
    review_id = await test_ingest_review()
    print(f"✅ Review ingested with ID: {review_id}\n")
    
    # Wait a moment for processing
    print("2. Waiting for processing...")
    time.sleep(5)
    
    # Test getting the review
    print("3. Getting review...")
    await test_get_review(review_id)
    print()
    
    # Test status
    print("4. Checking status...")
    await test_get_status(review_id)
    print()
    
    # Test listing
    print("5. Listing reviews...")
    await test_list_reviews()
    print()
    
    # Test stats
    print("6. Getting stats...")
    await test_stats()

if __name__ == "__main__":
    asyncio.run(main())