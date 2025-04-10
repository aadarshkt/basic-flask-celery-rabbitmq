from celery import Celery
from app.config import Config
import time
import os

# Initialize Celery
celery = Celery(
    "tasks", broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND
)

# Configure result expiration
celery.conf.update(
    result_expires=3600,  # Results automatically expire after 1 hour
    task_track_started=True,  # Track when tasks start
    task_track_received=True,  # Track when tasks are received
    broker_connection_retry_on_startup=True,  # Retry connecting to broker on startup
)


@celery.task(bind=True)
def process_file(self, filename):
    """
    A long-running task that processes a file.
    This is a sample task that simulates file processing with progress updates.

    Args:
        filename (str): The name of the file to process

    Returns:
        dict: A dictionary containing the processing results
    """
    # Simulate a long-running task
    total_steps = 10
    for i in range(total_steps):
        # Update task state
        self.update_state(
            state="PROGRESS", meta={"current": i + 1, "total": total_steps}
        )
        # Simulate work
        time.sleep(1)

    # Return the result
    return {
        "status": "completed",
        "filename": filename,
        "message": f"Successfully processed {filename}",
    }
