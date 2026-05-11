from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt
import uuid
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db import session as db_session
from app.db import models

router = APIRouter()

class GuestIn(BaseModel):
    name: Optional[str] = "Guest"

class GuestOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    saved: bool = False

@router.post("/guest", response_model=GuestOut)
def create_guest(request: Request, payload: GuestIn, db: Session = Depends(db_session.get_db)):
    """
    Create a guest access token for demo/trial users.
    
    - Generates a JWT token with limited expiration (DEMO_TOKEN_EXPIRE_MINUTES)
    - Persists token to Supabase/PostgreSQL for tracking
    - Returns token + confirmation flag
    
    Args:
        payload: Guest name (optional, defaults to "Guest")
    
    Returns:
        GuestOut: { access_token: str, token_type: str, saved: bool }
    """
    # 1. Create JWT token for demo/guest user
    try:
        expire_minutes = int(getattr(settings, "DEMO_TOKEN_EXPIRE_MINUTES", 15))
    except Exception:
        expire_minutes = 15

    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    jti = str(uuid.uuid4())
    token_payload = {
        "sub": payload.name or "guest",
        "jti": jti,
        "exp": expire
    }

    token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # 2. Persist token record to Postgres (Supabase)
    saved = False
    try:
        guest_row = models.GuestToken(
            name=payload.name,
            token=token,
            created_at=datetime.utcnow(),
            expires_at=expire,
            is_active=True
        )
        db.add(guest_row)
        db.commit()
        saved = True

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save guest token: {e}")

    return {"access_token": token, "token_type": "bearer", "saved": saved}

