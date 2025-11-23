@echo off
echo ========================================
echo M.A.R.S. Project - Quick Start
echo ========================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please either:
    echo   1. Install Python 3.11+ from python.org
    echo   2. OR use Docker: docker-compose up
    echo.
    pause
    exit /b 1
)

REM Check for Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo.
    echo Please either:
    echo   1. Install Node.js 18+ from nodejs.org
    echo   2. OR use Docker: docker-compose up
    echo.
    pause
    exit /b 1
)

REM Check if backend dependencies are installed
if not exist "backend\__pycache__" (
    echo Installing backend dependencies...
    cd backend
    pip install -r requirements.txt >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to install backend dependencies!
        echo Please run: cd backend ^&^& pip install -r requirements.txt
        pause
        exit /b 1
    )
    cd ..
)

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to install frontend dependencies!
        echo Please run: cd frontend ^&^& npm install
        pause
        exit /b 1
    )
    cd ..
)

echo Starting Backend Server...
start "M.A.R.S Backend" cmd /k "cd backend && python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start "M.A.R.S Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Both servers are starting!
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173 (or check the terminal)
echo.
echo Press any key to close this window...
pause >nul

