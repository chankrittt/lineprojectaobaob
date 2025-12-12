# Drive2 - AI-Powered LINE Storage System

AI-powered file storage system with LINE integration. Upload files via LINE, automatically organize with AI.

## Features

- 📤 **Easy Upload** - Send files through LINE
- 🤖 **Smart AI** - Auto-rename, summarize, and tag files
- 🔍 **Semantic Search** - Find files by meaning, not just keywords
- 📚 **Collections** - Organize and share files
- 🔐 **LINE Login** - No separate login required

## Tech Stack

**Backend**: FastAPI, PostgreSQL, Redis, Qdrant, MinIO
**AI**: Gemini AI (free tier)
**Frontend**: Next.js + LINE LIFF

## Quick Start

### 1. Setup Environment

```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with your credentials
```

### 2. Start Services

```bash
# Start infrastructure (PostgreSQL, Redis, Qdrant)
docker-compose up -d

# Install dependencies
cd backend
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Test connections
python test_connections.py
```

### 3. Run Application

```bash
# Start backend
python main.py

# API Docs: http://localhost:8000/docs
```

## Environment Variables

Configure these in `.env`:
- LINE credentials (channel secret, access token, LIFF ID)
- Gemini API key
- MinIO credentials
- Database credentials (auto-configured in docker-compose.yml)

## API Endpoints

- `POST /api/v1/auth/line` - LINE Login
- `POST /api/v1/files/upload` - Upload file
- `GET /api/v1/files` - List files
- `POST /api/v1/search/semantic` - Semantic search
- `POST /api/v1/webhook/line` - LINE webhook

See `/docs` for complete API documentation.

## Development

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Run tests
cd backend && pytest
```

## License

MIT
