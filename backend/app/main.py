from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.migration_helper import auto_migrate_on_startup
from app.routers import forensics, route, auth
from app.core.logging import setup_logging
from app.core.middleware import LoggingMiddleware
from app.core.aws_connection import init_aws
from app.services import storage
import logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(LoggingMiddleware)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://verijust.com",
]


# Set all CORS enabled origins
# In production, replace ["*"] with ["https://verijust.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

logger.info("VeriJust API started.")


@app.on_event("startup")
async def startup_migrations():
    """On app startup, auto-detect model changes and apply migrations.

    After migrations run we also validate the AWS connection so that
    misconfigured credentials cause an immediate failure.
    """
    try:
        # skip_autogenerate=True for production to speed up startup
        auto_migrate_on_startup(skip_autogenerate=False)
    except Exception as e:
        logger.error(f"Startup migration failed: {e}")
        raise

    # initialize AWS clients / test connection
    if not init_aws():
        # the init helper logs errors; raising will stop the server from
        # finishing startup so deployment knows something is wrong.
        raise RuntimeError("AWS initialization failed; check credentials")

    # Ensure S3 bucket exists and has secure defaults (encryption, lifecycle)
    try:
        storage.storage_service.ensure_bucket_configured()
    except Exception as e:
        logger.warning(f"Bucket configuration step failed: {e}")


@app.get("/")
def root():
    logger.info("Calling")
    return {"message": "Welcome to VeriJust API", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}



app.include_router(
    forensics.router,
    prefix="/forensics",
    tags=["Forensics"]
)


app.include_router(
    route.router,
    prefix="/users",
    tags=["Users"]
)


app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Auth"]
)