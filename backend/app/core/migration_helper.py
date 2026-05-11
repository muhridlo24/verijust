"""
Auto-migration helper: Detects model changes and generates migrations.
Useful for development—manually run migrations on startup to stay in sync.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
import logging
import os
import time

logger = logging.getLogger(__name__)

def run_command(cmd: list[str]) -> int:
    """Run a shell command and return the exit code."""
    try:
        result = subprocess.run(cmd, cwd=".", capture_output=True, text=True)
        if result.stdout:
            logger.info(result.stdout)
        if result.stderr:
            logger.error(result.stderr)
        return result.returncode
    except Exception as e:
        logger.error(f"Failed to run command {cmd}: {e}")
        return 1

def auto_generate_migrations():
    """
    Auto-generate a new migration if models have changed.
    Runs: alembic revision --autogenerate -m "auto_<timestamp>"
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    message = f"auto_{timestamp}"
    cmd = ["alembic", "revision", "--autogenerate", "-m", message]
    
    logger.info(f"Running auto-generate: {' '.join(cmd)}")
    return run_command(cmd)


def _latest_mtime_in_path(path: Path, pattern: str = "**/*.py") -> float:
    """Return the latest modification time for files under `path` matching pattern.
    If the path doesn't exist or contains no files, returns 0.
    """
    if not path.exists():
        return 0
    latest = 0.0
    for p in path.glob(pattern):
        try:
            m = p.stat().st_mtime
            if m > latest:
                latest = m
        except Exception:
            continue
    return latest

def apply_migrations():
    """
    Apply all pending migrations.
    Runs: alembic upgrade head
    """
    cmd = ["alembic", "upgrade", "head"]
    logger.info(f"Running migrations: {' '.join(cmd)}")
    return run_command(cmd)

def auto_migrate_on_startup(skip_autogenerate: bool = False):
    """
    On startup:
    1. (Optional) Run alembic revision --autogenerate to detect model changes
    2. Run alembic upgrade head to apply all pending migrations
    
    Args:
        skip_autogenerate: If True, skip autogenerate step (faster for CI/prod)
    """
    try:
        if not skip_autogenerate:
            logger.info("Checking for model changes in backend (debounced)...")

            # Debounce window (seconds). If backend files haven't changed
            # since the last alembic revision within this window, skip
            # autogeneration. This avoids spurious migrations when unrelated
            # files (frontend, docs) change.
            debounce_seconds = int(os.getenv("MIGRATION_DEBOUNCE_SECONDS", "60"))

            repo_root = Path('.')
            backend_app_path = repo_root / 'app'
            alembic_versions_path = repo_root / 'alembic' / 'versions'

            app_latest = _latest_mtime_in_path(backend_app_path)
            versions_latest = _latest_mtime_in_path(alembic_versions_path)

            logger.debug(f"app_latest={app_latest}, versions_latest={versions_latest}, debounce={debounce_seconds}")

            # If no alembic versions exist yet, run autogenerate to create initial migration
            if versions_latest == 0:
                logger.info("No existing alembic versions found — running autogenerate.")
                auto_generate_migrations()
            else:
                # Run autogenerate only if backend app files have a newer mtime
                # than the latest migration file by at least debounce_seconds.
                if app_latest > (versions_latest + debounce_seconds):
                    logger.info("Backend changes detected — running autogenerate.")
                    auto_generate_migrations()
                else:
                    logger.info("No backend changes detected — skipping autogenerate.")
        
        logger.info("Applying pending migrations...")
        apply_migrations()
        logger.info("✓ Database migrations completed successfully")
    except Exception as e:
        logger.error(f"✗ Migration failed: {e}")
        raise


def migrate_for_production():
    """
    Production mode: Only apply migrations (no autogenerate).
    Use this in CI/CD pipelines to speed up startup.
    """
    try:
        logger.info("Production mode: Applying pending migrations (no autogenerate)...")
        apply_migrations()
        logger.info("✓ Database migrations completed successfully")
    except Exception as e:
        logger.error(f"✗ Migration failed: {e}")
        raise

