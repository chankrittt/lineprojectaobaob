@echo off
echo ========================================
echo   Drive2 - Quick Start Script
echo ========================================
echo.

echo [1/5] Starting Docker containers...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start Docker containers
    pause
    exit /b 1
)
echo OK: Docker containers started
echo.

echo [2/5] Waiting for services to be ready...
timeout /t 10 /nobreak > nul
echo OK: Services should be ready
echo.

echo [3/5] Checking services status...
docker-compose ps
echo.

echo [4/5] Testing connections...
cd backend
python test_connections.py
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Some services failed to connect
    echo Please check the errors above
    echo.
)
cd ..
echo.

echo [5/5] Setup complete!
echo.
echo ========================================
echo   Next Steps:
echo ========================================
echo 1. Edit .env file with your credentials
echo 2. cd backend
echo 3. pip install -r requirements.txt
echo 4. alembic upgrade head
echo 5. python main.py
echo.
echo API Docs: http://localhost:8000/docs
echo Qdrant Dashboard: http://localhost:6333/dashboard
echo ========================================
echo.
pause
