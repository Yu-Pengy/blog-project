@echo off
title Cleanup Blog Application
echo ========================================
echo     Cleanup Blog Application
echo ========================================
echo.
echo This will stop and remove the blog application
echo.
pause

echo Stopping services...
docker-compose down

echo Removing application images...
docker rmi -f blog-backend:latest blog-frontend:latest 2>nul
docker rmi -f ghcr.io/yu-pengy/blog-backend:latest ghcr.io/yu-pengy/blog-frontend:latest 2>nul

echo.
echo Cleanup completed!
pause