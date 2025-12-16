@echo off
echo Starting Flower (Celery Monitoring)...
echo.

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Start Flower
echo Starting Flower on http://localhost:5555
celery -A app.workers.celery_app flower --port=5555

pause
