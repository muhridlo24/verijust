#!/bin/bash

# 1. Run Migrations
echo "Running Database Migrations..."
alembic upgrade head

# 2. Start the App
echo "Starting Uvicorn..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload