"""Flask application factory."""
from flask import Flask
from flask_cors import CORS
from app.config import config
from app.extensions import db, migrate, cache


def create_app(config_name='development'):
    """Create and configure the Flask application.

    Args:
        config_name: Configuration name ('development', 'production', 'testing')

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})

    # Import models for Flask-Migrate
    from app import models  # noqa: F401

    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    # Register CLI commands
    from app import cli
    app.cli.add_command(cli.seed_data_command)

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Warehouse Capacity Planner API'}, 200

    return app
