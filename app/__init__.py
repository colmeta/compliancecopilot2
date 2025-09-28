# ==============================================================================
# /app/__init__.py
# Final, correct version with all three blueprints registered and active.
# ==============================================================================

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
import os

# Create instances of our extensions, but don't initialize them yet
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    """
    The application factory. This function creates and configures the Flask app.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Initialize Extensions ---
    # Now we connect the extensions to our specific app instance
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Configure Flask-Login
    # If a user who is not logged in tries to access a protected page,
    # they will be redirected to the 'auth.login' endpoint.
    login_manager.login_view = 'auth.login'
    
    # This function is used by Flask-Login to load the current user from the database
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User  # Import here to avoid circular dependencies
        return User.query.get(int(user_id))

    # --- Register Blueprints ---
    # A blueprint is a self-contained set of routes and views (the "wings" of the fortress)
    from .auth.routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api.routes import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    # --- THIS BLOCK IS NOW ACTIVE ---
    # This imports the 'main' blueprint from our new file and registers it.
    from .main.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
