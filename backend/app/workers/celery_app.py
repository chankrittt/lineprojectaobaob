from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "drive2_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.tasks.file_processing",
        "app.workers.tasks.thumbnail",
        "app.workers.tasks.notifications",
    ]
)

# Celery Configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Bangkok",
    enable_utc=True,

    # Task execution
    task_track_started=True,
    task_time_limit=600,  # 10 minutes
    task_soft_time_limit=540,  # 9 minutes
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Results
    result_expires=3600,  # 1 hour
    result_persistent=True,
    result_backend_transport_options={
        'master_name': 'mymaster'
    },

    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,

    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,

    # Beat schedule (for periodic tasks)
    beat_schedule={
        'cleanup-old-tasks': {
            'task': 'app.workers.tasks.file_processing.cleanup_old_tasks',
            'schedule': 3600.0,  # Every hour
        },
    },
)


# Signal handlers for logging and monitoring
@task_prerun.connect
def task_prerun_handler(task_id, task, *args, **kwargs):
    """Log when task starts"""
    logger.info(f"Task {task.name}[{task_id}] started")


@task_postrun.connect
def task_postrun_handler(task_id, task, *args, retval=None, **kwargs):
    """Log when task completes"""
    logger.info(f"Task {task.name}[{task_id}] completed successfully")


@task_failure.connect
def task_failure_handler(task_id, exception, *args, **kwargs):
    """Log when task fails"""
    logger.error(f"Task [{task_id}] failed: {exception}")


if __name__ == "__main__":
    celery_app.start()
