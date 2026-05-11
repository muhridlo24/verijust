from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from app.db import session as db_session
from app.db import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

class UserContext(BaseModel):
    id: str
    name: str
    is_guest: bool = False
    is_demo: bool = False
    scopes: list[str] = []

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(db_session.get_db)
) -> UserContext:
    """
    Validate token and return user context.
    Supports both JWT tokens and guest tokens from the guest_tokens table.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Try to decode as JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        scopes: list = payload.get("scopes", [])
        
        if user_id is None:
            raise credentials_exception
            
        # 2. Return Context for regular user
        return UserContext(
            id=user_id,
            name=user_id,
            is_guest=False,
            is_demo=("demo_access" in scopes),
            scopes=scopes
        )
        
    except JWTError:
        # 2. Try to validate as guest token from database
        guest_token = db.query(models.GuestToken).filter(
            models.GuestToken.token == token,
            models.GuestToken.is_active == True,
            models.GuestToken.expires_at > datetime.utcnow()  # Not expired
        ).first()
        
        if guest_token:
            return UserContext(
                id=guest_token.id.hex,  # Convert UUID to string
                name=guest_token.name or "Guest",
                is_guest=True,
                is_demo=True,  # Guests have demo limits
                scopes=["guest_access"]
            )
        
        raise credentials_exception

def verify_usage_limits(
    request: Request, 
    user: UserContext = Depends(get_current_user)
) -> UserContext:
    """
    Blocks demo/guest users from uploading large files or spamming.
    """
    if user.is_demo or user.is_guest:
        # Rule 1: Content Length Check (Header based)
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > 5 * 1024 * 1024:  # 5MB Limit
            raise HTTPException(
                status_code=403, 
                detail="Demo limit exceeded: Max file size is 5MB. Please upgrade."
            )
            
    return user
