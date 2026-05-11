#!/bin/bash

# Migrations now run automatically on FastAPI startup via the migration_helper
# This ensures both hot-reload and auto-detection of model changes
echo "Starting Uvicorn with hot-reload enabled..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
