from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from jose import jwt, JWTError
from app.core.config import settings

# 1. Define the Key Function (Who are you?)
def get_rate_limit_key(request: Request) -> str:
    """
    Determines the unique ID for the user.
    - If Logged In: Returns User ID (from JWT)
    - If Guest: Returns IP Address
    """
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            # We do a 'unsafe' decode here just to get the ID quickly for Redis.
            # The real security check happens later in the Router dependency.
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload.get("sub", get_remote_address(request))
        except JWTError:
            pass
            
    # Fallback to IP address for anonymous users
    return get_remote_address(request)

# 2. Initialize Limiter
# We use the existing REDIS_URL from your config
limiter = Limiter(
    key_func=get_rate_limit_key,
    storage_uri=settings.CELERY_BROKER_URL, # Reusing Redis URL
    strategy="fixed-window" 
)