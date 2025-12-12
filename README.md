# Drive2 - AI-Powered LINE Storage System

คล้าย Google Drive แต่เก็บไฟล์บน LINE และใช้ AI จัดการไฟล์อัตโนมัติ

## Features

- **Easy Upload**: ส่งไฟล์ผ่าน LINE Group ตามปกติ
- **Smart Naming**: AI เปลี่ยนชื่อไฟล์อัตโนมัติให้สื่อความหมาย
- **Auto Tag & Summarize**: AI สรุปและติดแท็กไฟล์
- **Semantic Search**: ค้นหาไฟล์ด้วย AI (ไม่ต้องจำชื่อไฟล์)
- **No Login Required**: ใช้ LINE Official Account

## Tech Stack

### Backend
- **FastAPI** - Python web framework
- **PostgreSQL** - Main database
- **Redis** - Cache & Queue
- **Qdrant** - Vector database for semantic search
- **MinIO** - S3-compatible object storage
- **Gemini AI** - File analysis & embeddings

### Frontend
- **Next.js** - React framework
- **LINE LIFF** - LINE Frontend Framework

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- MinIO server (running at 172.27.15.49)
- LINE Official Account
- Gemini API Key

## Quick Start

### 1. Clone & Setup

```bash
cd drive2
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and fill in your credentials:
# - MINIO_ACCESS_KEY
# - MINIO_SECRET_KEY
# - GEMINI_API_KEY
# - LINE_CHANNEL_SECRET
# - LINE_CHANNEL_ACCESS_TOKEN
# - LINE_LIFF_ID
```

### 3. Start Infrastructure

```bash
# Start PostgreSQL, Redis, Qdrant
docker-compose up -d

# Check if all services are running
docker-compose ps
```

### 4. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 5. Test Connections

```bash
# Test all service connections
python test_connections.py
```

Expected output:
```
✅ PostgreSQL: Connected successfully
✅ Redis: Connected successfully
✅ Qdrant: Connected successfully
✅ MinIO: Connected successfully
✅ Gemini API: Connected successfully
🎉 All services connected successfully!
```

### 6. Run Database Migrations

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head
```

### 7. Start Development Server

```bash
# Start FastAPI
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit:
- API Docs: http://localhost:8000/docs
- Qdrant Dashboard: http://localhost:6333/dashboard

## Project Structure

```
drive2/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints/      # API endpoints
│   │   ├── core/
│   │   │   ├── config.py       # Configuration
│   │   │   └── database.py     # Database connection
│   │   ├── models/
│   │   │   └── database.py     # SQLAlchemy models
│   │   ├── services/
│   │   │   ├── ai_service.py       # Gemini AI
│   │   │   ├── storage_service.py  # MinIO
│   │   │   └── vector_service.py   # Qdrant
│   │   └── schemas/            # Pydantic schemas
│   ├── alembic/                # Database migrations
│   ├── main.py                 # FastAPI app
│   ├── requirements.txt
│   └── test_connections.py
├── frontend/                   # LINE LIFF app (Next.js)
├── docker-compose.yml
├── .env
└── README.md
```

## Services

### PostgreSQL
- **Port**: 5432
- **Database**: drive2_db
- **User**: drive2_user
- **Password**: drive2_password (change in .env)

### Redis
- **Port**: 6379
- **DB 0**: Cache
- **DB 1**: Celery queue

### Qdrant
- **Port**: 6333 (HTTP API)
- **Port**: 6334 (gRPC)
- **Dashboard**: http://localhost:6333/dashboard

### MinIO
- **External**: http://172.27.15.49:9000
- **Bucket**: drive2-files

## Development

### Run Tests
```bash
cd backend
pytest
```

### Check Logs
```bash
# View Docker logs
docker-compose logs -f

# Specific service
docker-compose logs -f postgres
docker-compose logs -f redis
docker-compose logs -f qdrant
```

### Stop Services
```bash
# Stop all Docker containers
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

## API Endpoints (Planned)

### Authentication
- `POST /api/v1/auth/line` - LINE Login

### Files
- `GET /api/v1/files` - List files
- `POST /api/v1/files/upload` - Upload file
- `GET /api/v1/files/:id` - Get file details
- `PUT /api/v1/files/:id` - Update file
- `DELETE /api/v1/files/:id` - Delete file
- `GET /api/v1/files/:id/download` - Download file

### Search
- `POST /api/v1/search/semantic` - Semantic search
- `GET /api/v1/search/text` - Full-text search

### Collections
- `GET /api/v1/collections` - List collections
- `POST /api/v1/collections` - Create collection
- `POST /api/v1/collections/:id/files/:fileId` - Add file to collection

### Webhook
- `POST /api/v1/webhook/line` - LINE webhook

## Troubleshooting

### MinIO Connection Failed
```bash
# Check if MinIO is accessible
curl http://172.27.15.49:9000

# Verify credentials in .env file
```

### PostgreSQL Connection Failed
```bash
# Check if container is running
docker-compose ps postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Gemini API Failed
```bash
# Verify API key is correct
# Check quota: https://aistudio.google.com/app/apikey
```

## Next Steps

1. Implement API endpoints (files, search, collections)
2. Create Celery workers for background jobs
3. Build LINE webhook handler
4. Develop LIFF frontend
5. Add authentication & authorization
6. Implement file processing pipeline

## License

MIT

## Contact

Issues: Create an issue on GitHub
