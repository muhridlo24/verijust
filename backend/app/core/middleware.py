import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

# Get the logger we setup earlier
logger = logging.getLogger("app.middleware")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Record Start Time
        start_time = time.time()
        
        # 2. Process the Request (This calls your router)
        try:
            response = await call_next(request)
        except Exception as e:
            # Log the error if the app crashes
            logger.error(f"Request failed: {request.method} {request.url.path} - Error: {e}")
            raise e # Re-raise so FastAPI handles the 500 error

        # 3. Calculate Duration
        process_time = (time.time() - start_time) * 1000  # Convert to ms
        formatted_process_time = "{0:.2f}".format(process_time)
        
        # 4. Log the details
        # Format: [METHOD] /path - StatusCode - Duration
        log_message = (
            f"[{request.method}] {request.url.path} "
            f"- {response.status_code} "
            f"- {formatted_process_time}ms"
        )
        
        logger.info(log_message)
        
        # 5. Add execution time to response headers (Optional but useful for debugging)
        response.headers["X-Process-Time"] = str(process_time)
        
        return response