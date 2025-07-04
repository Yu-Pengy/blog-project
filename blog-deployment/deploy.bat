@echo off
title Blog Application Deployment
echo ========================================
echo     Blog Application Deployment
echo ========================================
echo.
echo This script will download and start the blog application
echo Frontend: http://localhost
echo Backend:  http://localhost:5000
echo.
pause

echo [1/3] Downloading application images...
echo This may take a few minutes depending on your internet speed...
docker pull ghcr.io/yu-pengy/blog-backend:latest
docker pull ghcr.io/yu-pengy/blog-frontend:latest

echo.
echo [2/3] Preparing images for deployment...
docker tag ghcr.io/yu-pengy/blog-backend:latest blog-backend:latest
docker tag ghcr.io/yu-pengy/blog-frontend:latest blog-frontend:latest

echo.
echo [3/3] Starting blog application...
set DOCKER_BUILDKIT=0
docker-compose up -d

echo.
echo ========================================
echo    DEPLOYMENT SUCCESSFUL!
echo ========================================
echo.
echo Your blog is now running at:
echo   Frontend: http://localhost
echo   Backend:  http://localhost:5000
echo.
echo To stop the application, run: docker-compose down
echo To view logs, run: docker-compose logs -f
echo.
echo ========================================
docker-compose ps
echo.
echo Press any key to open the blog in your browser...
pause >nul
start http://localhost