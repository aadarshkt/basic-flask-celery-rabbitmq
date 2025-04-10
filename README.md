# Flask Celery RabbitMQ Application

This is a scalable Flask application that uses Celery with RabbitMQ for handling long-running file tasks.

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── celery_worker/
│   │   ├── __init__.py
│   │   └── tasks.py
│   └── config.py
├── requirements.txt
└── run.py
```

## Setup Instructions

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start RabbitMQ (make sure RabbitMQ is installed):

```bash
rabbitmq-server
```

4. Start the Flask application:

```bash
python run.py
```

5. In a separate terminal, start the Celery worker:

```bash
celery -A app.celery_worker.tasks worker --loglevel=info
```

## API Endpoints

- `POST /api/process-file`: Submit a file for processing
- `GET /api/task-status/<task_id>`: Check the status of a task

## Environment Variables

Create a `.env` file with the following variables:

```
FLASK_APP=run.py
FLASK_ENV=development
CELERY_BROKER_URL=amqp://localhost
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```
