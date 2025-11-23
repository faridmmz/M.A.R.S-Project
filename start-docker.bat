@echo off
echo ========================================
echo M.A.R.S. Project - Docker Start
echo ========================================
echo.

REM Check for Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed!
    echo.
    echo Please install Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop/
    echo.
    echo Docker Desktop must be RUNNING before you can use this script.
    echo.
    pause
    exit /b 1
)

echo Starting M.A.R.S. with Docker...
echo This will build and start both backend and frontend.
echo No Python or Node.js needed!
echo.
echo Press Ctrl+C to stop the servers
echo.

docker-compose up

