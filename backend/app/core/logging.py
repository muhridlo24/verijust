import logging
import sys
from app.core.config import settings

def setup_logging():
    """
    Configures the root logger to print nice timestamps and levels.
    """
    # 1. Define the format: "Time | Level | File | Message"
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # 2. Configure the ROOT logger
    # basicConfig is a quick helper that sets up a StreamHandler (Console output)
    logging.basicConfig(
        level=logging.INFO, # Capture everything INFO and above (WARNING, ERROR)
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout) # Send logs to Docker logs
        ]
    )

    # 3. Optional: Silence noisy libraries
    # Boto3 and Uvicorn can be very chatty. Let's quiet them down.
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

# Call this ONCE in your main.py