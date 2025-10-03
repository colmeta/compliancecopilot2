# ==============================================================================
# celery_worker.py
# Creates a Celery instance integrated with our Flask application factory.
# This allows background tasks to access the database and app context.
# ==============================================================================

from app import create_app
from celery import Celery

# Create a Flask app instance for the Celery worker
flask_app = create_app()

def make_celery(app):
    """
    Factory function that creates a Celery instance properly configured
    to work with our Flask application.
    """
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """
        Custom task class that ensures tasks run within Flask app context.
        This is critical for database access.
        """
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Create the final Celery instance using our factory
celery = make_celery(flask_app)
