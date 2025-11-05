# ==============================================================================
# app/__init__.py -- CORRECTED & FINAL WITH ERROR HANDLING & LOGGING
# The structure is now perfect for preventing circular imports.
# ==============================================================================

import logging
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate



# Step 1: Create the extension instances WITHOUT an app
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)
socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Validate required environment variables
    try:
        config_class.validate_required_env_vars()
    except ValueError as e:
        app.logger.error(f"Configuration error: {e}")
        raise

    # Step 2: Initialize the extensions WITH the app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # --- Configure Logging ---
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/clarity.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('CLARITY Engine startup')
    
    # This is where we break the circular import. We import the models
    # and routes AFTER the app and db are configured.
    from . import models
    from .auth.routes import auth as auth_blueprint
    from .api.routes import api as api_blueprint
    from .api.setup_routes import setup as setup_blueprint  # TEMPORARY SETUP
    from .api.multimodal_routes import multimodal as multimodal_blueprint  # PHASE 4
    from .api.collaboration_routes import collaboration as collaboration_blueprint  # PHASE 4B
    from .api.realtime_routes import realtime as realtime_blueprint  # PHASE 4B
    from .api.analytics_routes import analytics as analytics_blueprint  # PHASE 4C
    from .api.security_routes import security as security_blueprint  # PHASE 4D
    from .api.ai_optimization_routes import ai_optimization as ai_optimization_blueprint  # PHASE 4E
    from .api.api_management_routes import api_mgmt as api_mgmt_blueprint  # API Management
    from .main.routes import main as main_blueprint
    from .vault.routes import vault as vault_blueprint

    # --- Configure Flask-Login ---
    login_manager.login_view = 'auth.login'
    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    # --- Error Handlers ---
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f'404 error: {request.url}')
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'500 error: {error}')
        return render_template('errors/500.html'), 500

    @app.errorhandler(401)
    def unauthorized_error(error):
        app.logger.warning(f'401 error: {request.url}')
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f'403 error: {request.url}')
        return render_template('errors/403.html'), 403

    # --- Register Blueprints ---
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(setup_blueprint, url_prefix='/api/setup')  # TEMPORARY
    app.register_blueprint(multimodal_blueprint, url_prefix='/api/multimodal')  # PHASE 4
    app.register_blueprint(collaboration_blueprint, url_prefix='/api/collaboration')  # PHASE 4B
    app.register_blueprint(realtime_blueprint, url_prefix='/api/realtime')  # PHASE 4B
    app.register_blueprint(analytics_blueprint, url_prefix='/api/analytics')  # PHASE 4C
    app.register_blueprint(security_blueprint, url_prefix='/api/security')  # PHASE 4D
    app.register_blueprint(ai_optimization_blueprint, url_prefix='/api/ai-optimization')  # PHASE 4E
    app.register_blueprint(api_mgmt_blueprint)  # API Management (has its own prefix)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(vault_blueprint, url_prefix='/vault')
    
    # Landing page route
    @app.route('/')
    def landing():
        return render_template('landing.html')
    
    return app
