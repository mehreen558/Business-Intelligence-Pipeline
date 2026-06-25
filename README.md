# AI Customer Review Intelligence Platform

A complete system that collects, analyzes, and extracts insights from customer reviews using OpenAI with FastAPI, Redis, and SQLite.

## Features

- **Review Ingestion** - Accept reviews from multiple sources (Shopify, Amazon, etc.)
- **AI Analysis** - Sentiment analysis, topic extraction, entity recognition via OpenAI
- **Async Processing** - Redis queue with worker workers for non-blocking operations
- **Structured Output** - JSON responses from AI with confidence scores
- **SQLite Storage** - Lightweight database with JSON support for flexible schemas
- **REST API** - FastAPI endpoints for all operations
- **Dashboard Ready** - Designed for React/Next.js frontend integration

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy + SQLite
- Redis + RQ (Redis Queue)
- Claude/OpenAI APIs
- Pydantic for validation

## Quick Start

```bash
# Clone
git clone <repository-url>
cd ai-review-intelligence

# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Environment
cp .env.example .env
# Add your API keys to .env

# Initialize DB
python scripts/init_db.py

# Start services (3 terminals)
redis-server                          # Terminal 1
uvicorn app.main:app --reload        # Terminal 2  
python app/worker.py                  # Terminal 3
```

## Environment Variables

```env
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite:///./reviews.db
API_PORT=8000
```

## Project Structure

```
.
├── app/
│   ├── api/           # FastAPI routes
│   ├── core/          # Config & dependencies
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   ├── workers/       # RQ worker functions
│   └── utils/         # Helpers
├── scripts/           # Management scripts
├── tests/             # Unit tests
├── requirements.txt
├── docker-compose.yml
└── .env.example
```
## Deployment

### Docker
```bash
docker-compose up -d
docker-compose up -d --scale worker=4
```

### Production Checklist
- [ ] Set environment variables
- [ ] Configure logging
- [ ] Setup database backups
- [ ] Enable HTTPS
- [ ] Implement rate limiting
- [ ] Add monitoring

## Testing

```bash
pytest
pytest --cov=app tests/
```

## License

MIT
