@echo off
echo ========================================
echo M.A.R.S. Project - Dependency Checker
echo ========================================
echo.

set MISSING=0

REM Check for Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python is NOT installed
    echo     Download from: https://www.python.org/downloads/
    set MISSING=1
) else (
    python --version
    echo [OK] Python is installed
)
echo.

REM Check for Node.js
echo Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [X] Node.js is NOT installed
    echo     Download from: https://nodejs.org/
    set MISSING=1
) else (
    node --version
    echo [OK] Node.js is installed
)
echo.

REM Check for Docker
echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [X] Docker is NOT installed
    echo     Download from: https://www.docker.com/products/docker-desktop/
    echo     NOTE: Docker is the EASIEST way - no Python/Node.js needed!
) else (
    docker --version
    echo [OK] Docker is installed - You can use: docker-compose up
)
echo.

REM Check for pip
echo Checking pip (Python package manager)...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [X] pip is NOT available
    set MISSING=1
) else (
    echo [OK] pip is available
)
echo.

REM Check for npm
echo Checking npm (Node package manager)...
npm --version >nul 2>&1
if errorlevel 1 (
    echo [X] npm is NOT available
    set MISSING=1
) else (
    npm --version
    echo [OK] npm is available
)
echo.

echo ========================================
if %MISSING%==1 (
    echo RESULT: Missing dependencies detected!
    echo.
    echo RECOMMENDATION: Use Docker instead!
    echo   1. Install Docker Desktop
    echo   2. Run: docker-compose up
    echo   3. No Python or Node.js needed!
) else (
    echo RESULT: All dependencies are installed!
    echo You can run: start.bat
)
echo ========================================
echo.
pause

