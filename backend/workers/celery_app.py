"""
Celery application configuration
"""
from celery import Celery
from core.config import settings

# Create Celery app
celery_app = Celery(
    'creative_analysis',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['workers.tasks.analysis_tasks']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Task routes (optional: route different tasks to different queues)
celery_app.conf.task_routes = {
    'workers.tasks.analysis_tasks.*': {'queue': 'analysis'},
}
