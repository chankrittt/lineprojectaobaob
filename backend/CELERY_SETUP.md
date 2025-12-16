# Celery Background Workers Setup

This document explains how to run and use the Celery background processing system for Drive2.

## Overview

Celery is used for:
- **Async file processing**: AI analysis runs in background
- **Thumbnail generation**: Generate thumbnails for images
- **Notifications**: Send LINE notifications when processing completes
- **Periodic tasks**: Cleanup old tasks, send daily summaries

## Architecture

```
┌─────────────┐
│   FastAPI   │  ← User uploads file
│   Backend   │  → Dispatches Celery task
└─────────────┘  → Returns immediately

       ↓

┌─────────────┐
│    Redis    │  ← Task queue (broker)
│   (Broker)  │  ← Result backend
└─────────────┘

       ↓

┌─────────────┐
│   Celery    │  ← Worker processes tasks
│   Worker    │  → AI processing
└─────────────┘  → Thumbnail generation
                 → Notifications

       ↓

┌─────────────┐
│  PostgreSQL │  ← Update file status
│   Qdrant    │  ← Store embeddings
│   MinIO     │  ← Store thumbnails
└─────────────┘
```

## Quick Start

### Using Docker (Recommended)

```bash
# Start all services including Celery workers
docker-compose up -d

# View logs
docker-compose logs -f celery_worker

# Stop services
docker-compose down
```

Services:
- **celery_worker**: Main worker for processing tasks
- **celery_beat**: Scheduler for periodic tasks
- **flower**: Web UI for monitoring (http://localhost:5555)

### Manual Setup (Development)

#### 1. Start Redis

```bash
# If using Docker for infrastructure only
docker-compose up -d redis postgres qdrant
```

#### 2. Start Celery Worker

**Windows:**
```bash
cd backend
start_celery.bat
```

**Linux/Mac:**
```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

#### 3. Start Celery Beat (Optional - for periodic tasks)

**Windows:**
```bash
celery -A app.workers.celery_app beat --loglevel=info
```

**Linux/Mac:**
```bash
celery -A app.workers.celery_app beat --loglevel=info
```

#### 4. Start Flower Monitoring (Optional)

**Windows:**
```bash
start_flower.bat
```

**Linux/Mac:**
```bash
celery -A app.workers.celery_app flower --port=5555
```

Then open: http://localhost:5555

## Tasks

### File Processing Tasks

#### `process_uploaded_file`
- **Description**: Main task for processing uploaded files
- **Triggered**: Automatically when file is uploaded via API
- **What it does**:
  1. Download file from MinIO
  2. Extract text content
  3. Run AI analysis (filename, summary, tags, embedding)
  4. Update database
  5. Store embedding in Qdrant

#### `generate_ai_metadata`
- **Description**: Generate AI metadata for a file
- **Can be called independently**

#### `reprocess_file`
- **Description**: Reprocess a failed file
- **Triggered**: Via `/api/v1/files/{file_id}/reprocess` endpoint

#### `cleanup_old_tasks`
- **Description**: Cleanup stuck files and old task results
- **Triggered**: Automatically every hour (Celery Beat)

### Thumbnail Tasks

#### `generate_thumbnail`
- **Description**: Generate thumbnail for image files
- **What it does**:
  1. Download image from MinIO
  2. Create 300x300 thumbnail
  3. Upload to MinIO (thumbnails/ folder)
  4. Update database with thumbnail_path

### Notification Tasks

#### `send_processing_complete`
- **Description**: Send LINE notification when processing completes
- **TODO**: Implement LINE Flex Message integration

#### `send_processing_failed`
- **Description**: Send notification when processing fails

#### `send_storage_quota_alert`
- **Description**: Send alert when storage quota is high

#### `send_daily_summary`
- **Description**: Send daily summary of files uploaded

## API Endpoints

### Upload File
```http
POST /api/v1/files/upload
```
- Returns immediately with `file_id`
- File is processed in background
- Status: `pending` → `processing` → `completed` or `failed`

### Check Processing Status
```http
GET /api/v1/files/{file_id}/status
```
- Returns current processing status
- Includes AI results when completed

### Reprocess File
```http
POST /api/v1/files/{file_id}/reprocess
```
- Retry processing for failed files
- Resets status to `pending` and dispatches new task

## Monitoring

### Using Flower

1. Start Flower: `start_flower.bat` or via Docker
2. Open: http://localhost:5555
3. View:
   - Active tasks
   - Task history
   - Worker status
   - Task statistics
   - Success/failure rates

### Using Celery CLI

```bash
# Check active tasks
celery -A app.workers.celery_app inspect active

# Check scheduled tasks
celery -A app.workers.celery_app inspect scheduled

# Check registered tasks
celery -A app.workers.celery_app inspect registered

# Get worker stats
celery -A app.workers.celery_app inspect stats

# Purge all tasks
celery -A app.workers.celery_app purge
```

### Logs

Worker logs show:
- Task start/completion
- Processing progress
- Errors and retries
- Performance metrics

## Configuration

### Celery Settings (`config.py`)

```python
CELERY_BROKER_URL = "redis://localhost:6379/1"
CELERY_RESULT_BACKEND = "redis://localhost:6379/1"
```

### Worker Settings (`celery_app.py`)

```python
task_time_limit = 600          # 10 minutes max
task_soft_time_limit = 540     # 9 minutes warning
task_max_retries = 3           # Retry failed tasks 3 times
task_default_retry_delay = 60  # Wait 1 minute before retry
```

## Troubleshooting

### Worker not processing tasks

1. Check Redis is running:
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

2. Check worker logs for errors

3. Verify Celery can connect to Redis:
   ```bash
   celery -A app.workers.celery_app inspect ping
   ```

### Tasks stuck in "processing"

- Automatic cleanup runs every hour
- Or manually mark as failed:
  ```sql
  UPDATE files SET processing_status = 'failed'
  WHERE processing_status = 'processing'
  AND uploaded_at < NOW() - INTERVAL '1 hour';
  ```

### High memory usage

- Reduce worker concurrency:
  ```bash
  celery -A app.workers.celery_app worker --concurrency=2
  ```

- Enable worker restarts after N tasks:
  ```python
  worker_max_tasks_per_child = 1000
  ```

## Performance Tips

1. **Concurrency**: Adjust based on CPU cores
   - 4 cores → `--concurrency=4`
   - CPU-bound tasks → `--concurrency=cores`
   - I/O-bound tasks → `--concurrency=cores*2`

2. **Prefetch**: Control how many tasks worker fetches
   ```bash
   --prefetch-multiplier=4
   ```

3. **Task routing**: Create dedicated workers for specific tasks
   ```bash
   celery -A app.workers.celery_app worker -Q ai_processing
   celery -A app.workers.celery_app worker -Q thumbnails
   ```

## Development

### Adding a new task

1. Create task in `app/workers/tasks/`:
   ```python
   @celery_app.task(name="app.workers.tasks.my_task")
   def my_task(arg1, arg2):
       # Task logic
       return result
   ```

2. Add to `celery_app.py` includes:
   ```python
   include=[
       "app.workers.tasks.file_processing",
       "app.workers.tasks.my_new_tasks",
   ]
   ```

3. Dispatch from API:
   ```python
   from app.workers.tasks.my_new_tasks import my_task

   task = my_task.delay(arg1, arg2)
   task_id = task.id
   ```

### Testing tasks

```python
# Run task synchronously (for testing)
result = my_task(arg1, arg2)

# Run async but wait for result
result = my_task.delay(arg1, arg2).get(timeout=10)
```

## Production Deployment

1. **Use systemd** (Linux):
   ```ini
   [Unit]
   Description=Celery Worker
   After=network.target

   [Service]
   Type=forking
   User=www-data
   WorkingDirectory=/app/backend
   ExecStart=/usr/local/bin/celery -A app.workers.celery_app worker
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. **Use supervisor** (alternative):
   ```ini
   [program:celery-worker]
   command=celery -A app.workers.celery_app worker --loglevel=info
   directory=/app/backend
   autostart=true
   autorestart=true
   ```

3. **Use Docker** (recommended):
   - Already configured in `docker-compose.yml`
   - Automatic restarts
   - Isolated environment

## Next Steps

- [ ] Implement LINE Flex Message notifications
- [ ] Add thumbnail generation for PDFs (requires pdf2image)
- [ ] Add video thumbnail generation (requires ffmpeg)
- [ ] Implement rate limiting for Gemini API
- [ ] Add batch processing for multiple files
- [ ] Create admin dashboard for task management

## Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Flower Documentation](https://flower.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)
