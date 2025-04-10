from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.api.routes import api


def create_app(config_class=Config):
    """
    Application factory function.
    Creates and configures the Flask application.

    Args:
        config_class: The configuration class to use

    Returns:
        Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS
    CORS(app)

    # Register blueprints
    app.register_blueprint(api, url_prefix="/api")

    # Create upload folder if it doesn't exist
    import os

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    return app
