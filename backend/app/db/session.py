from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 1. Create the Engine
# We use connection pooling to be efficient.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Checks if connection is alive before using it
    pool_size=20,        # Max connections in the pool
    max_overflow=0
)

# 2. Create the Session Factory
# Each request will get a fresh session from this factory.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Dependency Injection
# This is what you use in your routers: "db: Session = Depends(get_db)"
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()