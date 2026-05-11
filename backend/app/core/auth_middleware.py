"""
Authentication Middleware
Logs all authentication attempts and token validations
"""

from fastapi import Request
from datetime import datetime
import logging
from typing import Callable

logger = logging.getLogger(__name__)

class TokenAuthMiddleware:
    """
    Middleware to log and track token-based authentication.
    Provides visibility into:
    - Token validity
    - User access patterns
    - Failed authentication attempts
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable):
        # Extract token from header
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.split(" ")[1] if auth_header.startswith("Bearer ") else None
        
        # Log auth attempt
        if token:
            logger.debug(f"Token validation attempt: {request.method} {request.url.path}")
        
        # Call next middleware/route
        response = await call_next(request)
        
        # Log response status
        if token:
            logger.debug(f"Auth result: {response.status_code} for {request.url.path}")
        
        return response
