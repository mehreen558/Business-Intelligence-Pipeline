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


## **Quick Start**

### 1. Clone the Repository
```bash
git clone https://github.com/mehreen558/Business-Intelligence-Pipeline.git
cd CustomerReviews-Pipeline
```

### 2. Start Backend (Docker)
```bash
docker compose up -d
```

### 3. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000/docs

---

## 📋 **Prerequisites**

- Docker Desktop
- Node.js 18+
- Python 3.11+

---

## 🛠️ **Development Mode**

```bash
# Backend (without Docker)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

---

##  **Environment Variables**

Create `.env` file in root:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/reviews
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your_key_here
AI_PROVIDER=openai
```

## License

MIT
