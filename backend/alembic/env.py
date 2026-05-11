import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# ----------------------------------------------------------------------
# 1. ADD YOUR PROJECT PATH (Crucial for Docker)
# ----------------------------------------------------------------------
sys.path.append(os.getcwd())

# ----------------------------------------------------------------------
# 2. IMPORT YOUR MODELS & CONFIG
# ----------------------------------------------------------------------
from app.core.config import settings  # Gets DATABASE_URL
from app.db.base import Base          # Gets the Base class
from app.db.models import * # Force load all models so Base knows them!

# ----------------------------------------------------------------------
# 3. SET THE METADATA (This fixes your error!)
# ----------------------------------------------------------------------
target_metadata = Base.metadata

# ----------------------------------------------------------------------
# Standard Alembic Config
# ----------------------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata, # <--- MUST BE HERE
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    
    # 1. Get config from .ini
    configuration = config.get_section(config.config_ini_section) or {}
    
    # 2. OVERRIDE URL with env var
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata # <--- AND HERE (This was likely missing)
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()