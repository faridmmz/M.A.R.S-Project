#!/bin/bash

echo "========================================"
echo "M.A.R.S. Project - Docker Start"
echo "========================================"
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed!"
    echo ""
    echo "Please install Docker Desktop from:"
    echo "https://www.docker.com/products/docker-desktop/"
    echo ""
    echo "Docker Desktop must be RUNNING before you can use this script."
    echo ""
    exit 1
fi

# Check if Docker daemon is running
if ! docker info > /dev/null 2>&1; then
    echo "[ERROR] Docker daemon is not running!"
    echo ""
    echo "Please start Docker Desktop and try again."
    echo ""
    exit 1
fi

echo "Starting M.A.R.S. with Docker..."
echo "This will build and start both backend and frontend."
echo "No Python or Node.js needed!"
echo ""
echo "Press Ctrl+C to stop the servers"
echo ""

docker-compose up

