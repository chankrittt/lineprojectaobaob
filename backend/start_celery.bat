@echo off
echo Starting Celery Worker for Drive2...
echo.

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Start Celery Worker
echo Starting Celery Worker...
celery -A app.workers.celery_app worker --loglevel=info --pool=solo --concurrency=1

pause
