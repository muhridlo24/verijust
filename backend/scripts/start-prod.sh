#!/bin/bash

# Production start script: Skip autogenerate for faster startup
# Run migrations manually in CI/CD pipeline

echo "Starting Uvicorn (Production mode - no auto-reload)..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
