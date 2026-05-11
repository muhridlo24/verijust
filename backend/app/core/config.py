from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # --- Core API Config ---
    PROJECT_NAME: str = "VeriJust API"
    API_V1_STR: str = "/api/v1"
    
    # --- Security & Auth (User Management) ---
    SECRET_KEY: str  # Run 'openssl rand -hex 32' to generate this
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Standard JWT expiration

    # --- Database (PostgreSQL) ---
    DATABASE_URL: str  # e.g., postgresql+asyncpg://user:pass@localhost/dbname

    # --- AWS General Config ---
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"

    # --- AWS Services Specifics ---
    # Storage (S3)
    S3_BUCKET_NAME: str = "verijust-uploads"
    S3_PRESIGNED_URL_EXPIRATION: int = 3600  # 1 hour
    # Upload limits (MB)
    UPLOAD_MAX_SIZE_MB: int = 200
    GUEST_UPLOAD_MAX_SIZE_MB: int = 5
    
    # AI (Bedrock / Nova)
    # Check AWS Console for exact ID (e.g., 'amazon.nova-pro-v1:0')
    BEDROCK_MODEL_ID: str = "amazon.nova-pro-v1:0" 

    # --- Background Tasks (Celery + Redis) ---
    # Default to local Redis if not set
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # --- Emailing (SMTP) ---
    # Use these for SendGrid, AWS SES (SMTP interface), or Gmail
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: str = "noreply@verijust.ai"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    # --- Pydantic Config ---
    # This automatically loads the .env file
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_ignore_empty=True,
        extra="ignore" # Ignores extra fields in .env so app doesn't crash
    )

settings = Settings()