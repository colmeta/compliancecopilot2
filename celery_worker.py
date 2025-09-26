# celery_worker.py
from celery import Celery
import os

# Set up Celery. 'tasks' is the default name for the module where your tasks live.
# The 'broker' is Redis, which acts as the mailbox for jobs.
# The 'backend' is also Redis, where the results of the jobs are stored.
celery_app = Celery(
    'tasks',
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ensure we use JSON for tasks
    result_serializer='json',
)
