# ==============================================================================
# celery_worker.py
# This file initializes and configures the Celery application.
# ==============================================================================

from celery import Celery
import os

# Create the Celery instance.
# 'tasks' is the name of the module where your background task functions are defined.
celery_app = Celery(
    'tasks',
    # The broker is the message queue (Redis) that holds jobs.
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    # The backend is where Celery stores the results of the jobs.
    backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Optional configuration to improve robustness
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
