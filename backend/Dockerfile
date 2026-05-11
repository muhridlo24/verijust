# 1. Base Image (Official Python 3.10 Slim - smaller & faster)
FROM python:3.11

# 2. Set Environment Variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files
# PYTHONUNBUFFERED: Ensures logs are flushed immediately (vital for Docker logs)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Set Work Directory
WORKDIR /app

# 4. Install System Dependencies (The "OS" level stuff)
# We need 'ffmpeg' for audio and 'gcc' for building some python libs
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python Dependencies
# We copy requirements first to leverage Docker Cache (faster builds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your application code
COPY . .

# 7. Create a non-root user for security (Optional but recommended)
# RUN useradd -m appuser && chown -R appuser /app
# USER appuser

# 8. Define the command to run the app
# (We will override this in docker-compose for the Celery worker)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]