import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_ingest_review():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/reviews/",
            json={
                "source": "shopify",
                "rating": 5,
                "review_text": "Great product!"
            }
        )
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "queued"
        assert "id" in data