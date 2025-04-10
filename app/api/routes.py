from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from app.config import Config
from app.celery_worker.tasks import process_file

# Create a Blueprint for the API
api = Blueprint("api", __name__)


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    )

@api.route("/")
def get_request():
    return jsonify({"message": "Hello, World!"}), 200

@api.route("/process-file", methods=["POST"])
def submit_file():
    """
    Endpoint to submit a file for processing.
    Accepts multipart form data with a file field.
    """
    # Check if a file was uploaded
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    # Check if a file was selected
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Check if the file type is allowed
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    # Secure the filename and save the file
    filename = secure_filename(file.filename)
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

    # Create upload folder if it doesn't exist
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    # Save the file
    file.save(filepath)

    # Start the Celery task
    task = process_file.delay(filename)

    return jsonify({"message": "File uploaded successfully", "task_id": task.id}), 202


@api.route("/task-status/<task_id>", methods=["GET"])
def get_task_status(task_id):
    """
    Endpoint to check the status of a task.

    Args:
        task_id (str): The ID of the task to check
    """
    task = process_file.AsyncResult(task_id)

    try:
        if task.state == "PENDING":
            response = {"state": task.state, "status": "Task is pending..."}
        elif task.state == "PROGRESS":
            response = {
                "state": task.state,
                "status": "Task is in progress...",
                "current": task.info.get("current", 0),
                "total": task.info.get("total", 0),
            }
        elif task.state == "SUCCESS":
            # Get the result and clean up
            result = task.get()  # Get result before forgetting
            task.forget()  # Clean up the result
            response = {
                "state": "SUCCESS",
                "status": "Task completed successfully",
                "result": result,
            }
        elif task.state == "FAILURE":
            # Get error info and clean up
            error = str(task.info)
            task.forget()
            response = {"state": "FAILURE", "status": error}
        else:
            response = {"state": task.state, "status": str(task.info)}

        return jsonify(response)
    except Exception as e:
        # Always clean up on errors
        task.forget()
        return jsonify({"state": "ERROR", "status": str(e)}), 500
