# ==============================================================================
# app/__init__.py
# CLARITY Platform - Flask Application Factory - STAGED DEPLOYMENT
# ==============================================================================

import logging
import os
from flask import Flask, render_template, request, jsonify
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

    # Validate required environment variables (but don't crash if missing)
    try:
        config_class.validate_required_env_vars()
    except (ValueError, AttributeError) as e:
        app.logger.warning(f"Configuration warning: {e}")
        # Don't crash - use defaults

    # Step 2: Initialize the extensions WITH the app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    CORS(app, origins=['*'])  # Allow all for now
    
    # --- Configure Logging ---
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/clarity.log')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('CLARITY Engine startup')

    # --- Register Blueprints (STAGED - Only Core Ones First) ---
    
    # Core Routes (Required) - MUST BE FIRST to handle root route
    try:
        from .main.routes import main as main_blueprint
        app.register_blueprint(main_blueprint)  # NO url_prefix - handles root /
        app.logger.info("✅ Main routes registered (handling root /)")
    except Exception as e:
        app.logger.error(f"❌ Could not load main routes: {e}")
    
    # API Routes (Required)
    try:
        from .api.routes import api as api_blueprint
        app.register_blueprint(api_blueprint, url_prefix='/api')
        app.logger.info("✅ API routes registered")
    except Exception as e:
        app.logger.error(f"❌ Could not load API routes: {e}")
    
    # Auth (Required)
    try:
        from .auth.routes import auth as auth_blueprint
        app.register_blueprint(auth_blueprint, url_prefix='/auth')
        app.logger.info("✅ Auth routes registered")
    except Exception as e:
        app.logger.error(f"❌ Could not load auth routes: {e}")
    
    # Vault (Optional but important)
    try:
        from .vault.routes import vault as vault_blueprint
        app.register_blueprint(vault_blueprint, url_prefix='/vault')
        app.logger.info("✅ Vault routes registered")
    except Exception as e:
        app.logger.warning(f"⚠️ Vault routes not available: {e}")
    
    # Funding Readiness Engine (NEW - Outstanding Edition)
    try:
        from .api.funding_routes import funding_api as funding_blueprint
        from .api.funding_interactive_routes import funding_interactive as funding_interactive_blueprint
        app.register_blueprint(funding_blueprint)
        app.register_blueprint(funding_interactive_blueprint)
        app.logger.info("✅ Funding Readiness Engine registered (Outstanding Edition)")
    except Exception as e:
        app.logger.warning(f"⚠️ Funding engine not available: {e}")
    
    # API Management (NEW)
    try:
        from .api.api_management_routes import api_mgmt as api_mgmt_blueprint
        app.register_blueprint(api_mgmt_blueprint)
        app.logger.info("✅ API Management registered")
    except Exception as e:
        app.logger.warning(f"⚠️ API Management not available: {e}")
    
    # Additional Phase 4 features (Optional - load if available)
    optional_blueprints = [
        ('multimodal', 'api.multimodal_routes', '/api/multimodal'),
        ('collaboration', 'api.collaboration_routes', '/api/collaboration'),
        ('realtime', 'api.realtime_routes', '/api/realtime'),
        ('analytics', 'api.analytics_routes', '/api/analytics'),
        ('security', 'api.security_routes', '/api/security'),
        ('ai_optimization', 'api.ai_optimization_routes', '/api/ai-optimization'),
    ]
    
    for name, module_path, url_prefix in optional_blueprints:
        try:
            module = __import__(f'app.{module_path}', fromlist=[name])
            blueprint = getattr(module, name)
            app.register_blueprint(blueprint, url_prefix=url_prefix)
            app.logger.info(f"✅ {name.title()} routes registered")
        except Exception as e:
            app.logger.debug(f"⏸️  {name.title()} routes not available: {e}")
    
    # Root route is handled by main blueprint (main.homepage)
    
    # --- Health Check ---
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'mode': 'production'})
    
    # --- Error Handlers ---
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    app.logger.info("CLARITY Engine initialized successfully!")
    
    return app
