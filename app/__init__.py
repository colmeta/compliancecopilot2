# ==============================================================================
# app/__init__.py -- CORRECTED & FINAL
# The structure is now perfect for preventing circular imports.
# ==============================================================================

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate



# Step 1: Create the extension instances WITHOUT an app
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Step 2: Initialize the extensions WITH the app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # This is where we break the circular import. We import the models
    # and routes AFTER the app and db are configured.
    from . import models
    from .auth.routes import auth as auth_blueprint
    from .api.routes import api as api_blueprint
    from .api.setup_routes import setup as setup_blueprint  # TEMPORARY SETUP
    from .main.routes import main as main_blueprint

    # --- Configure Flask-Login ---
    login_manager.login_view = 'auth.login'
    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    # --- Register Blueprints ---
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(setup_blueprint, url_prefix='/api/setup')  # TEMPORARY
    app.register_blueprint(main_blueprint)
    
    return app
