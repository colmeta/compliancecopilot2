# ==============================================================================
# app/__init__.py
# This is the application factory. It creates and configures the Flask app.
# ==============================================================================

from flask import Flask
from config import Config
from .models import db  # Import the db instance from models.py
from flask_migrate import Migrate

def create_app(config_class=Config):
    """Creates and configures an instance of the Flask application."""
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # --- Initialize Extensions ---
    # Link the SQLAlchemy object to our Flask app
    db.init_app(app)
    # Link Flask-Migrate to our app and database
    migrate = Migrate(app, db)
    
    # --- Register Blueprints (we will add these later for auth and api routes) ---
    # For now, we will add a simple test route here.
    @app.route('/test-db')
    def test_db():
        try:
            db.session.execute('SELECT 1')
            return '<h1>Database connection is working.</h1>'
        except Exception as e:
            return f'<h1>Database connection failed: {e}</h1>'
            
    return app
