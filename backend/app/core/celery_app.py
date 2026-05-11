from celery import Celery
from app.core.config import settings

# 1. Initialize the Celery App
# 'verijust_worker' is just a name for the worker process
celery_app = Celery("verijust_worker")

# 2. Load Config from your settings
# This tells Celery where Redis is (broker_url)
celery_app.conf.broker_url = settings.CELERY_BROKER_URL
celery_app.conf.result_backend = settings.CELERY_RESULT_BACKEND

# 3. Optimization Settings (Recommended for Production)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_time_limit=300,  # Kill task if runs longer than 5 mins
)