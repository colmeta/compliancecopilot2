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
    
    # CORS configuration for Vercel frontend
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:3000",  # Local development
                "https://*.vercel.app",    # Vercel deployments
                "https://clarity-frontend.vercel.app",  # Production frontend
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Range", "X-Content-Range"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })
    
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
    
    # CRITICAL: Simple health check endpoint for Render (BEFORE blueprints)
    @app.route('/health', methods=['GET', 'HEAD'])
    def health_check_endpoint():
        """Instant health check - no dependencies"""
        return jsonify({'status': 'ok', 'service': 'clarity', 'ready': True}), 200

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
    
    # Simple Test Routes (NO AUTH - FOR TESTING)
    try:
        from .api.simple_test_routes import simple_test as simple_test_blueprint
        app.register_blueprint(simple_test_blueprint)
        app.logger.info("✅ Simple test routes registered (NO AUTH)")
    except Exception as e:
        app.logger.error(f"❌ Could not load simple test routes: {e}")
    
    # Quick Test Routes (INSTANT RESPONSE - NO EMAIL/CELERY)
    try:
        from .api.quick_test_routes import quick_test as quick_test_blueprint
        app.register_blueprint(quick_test_blueprint)
        app.logger.info("✅ Quick test routes registered (INSTANT)")
    except Exception as e:
        app.logger.error(f"❌ Could not load quick test routes: {e}")
    
    # Instant Routes (FREE TIER OPTIMIZED)
    try:
        from .api.instant_routes import instant as instant_blueprint
        app.register_blueprint(instant_blueprint)
        app.logger.info("✅ Instant routes registered (FREE TIER)")
    except Exception as e:
        app.logger.error(f"❌ Could not load instant routes: {e}")
    
    # Email Test Routes (NO AUTH - FOR TESTING EMAIL)
    try:
        from .api.email_test_routes import email_test as email_test_blueprint
        app.register_blueprint(email_test_blueprint)
        app.logger.info("✅ Email test routes registered (TEST EMAIL)")
    except Exception as e:
        app.logger.error(f"❌ Could not load email test routes: {e}")
    
    # Real Analysis Routes (REAL AI - NO SIMULATIONS)
    try:
        from .api.real_analysis_routes import real_analysis as real_analysis_blueprint
        app.register_blueprint(real_analysis_blueprint)
        app.logger.info("✅ Real AI analysis routes registered (GEMINI)")
    except Exception as e:
        app.logger.error(f"❌ Could not load real analysis routes: {e}")
    
    # Real Funding Routes (REAL DOCUMENT GENERATION)
    try:
        from .api.real_funding_routes import real_funding as real_funding_blueprint
        app.register_blueprint(real_funding_blueprint)
        app.logger.info("✅ Real funding document generator registered (GEMINI PRO)")
    except Exception as e:
        app.logger.error(f"❌ Could not load real funding routes: {e}")
    
    # Real Funding V2 (COMPLETE WORKFLOW: Generate→Convert→Package→Email)
    try:
        from .api.real_funding_routes_v2 import real_funding_v2 as real_funding_v2_blueprint
        app.register_blueprint(real_funding_v2_blueprint)
        app.logger.info("✅ Complete funding workflow V2 registered (PRESIDENTIAL QUALITY)")
    except Exception as e:
        app.logger.error(f"❌ Could not load funding V2 routes: {e}")
    
    # OCR Routes (Extract text from images/documents - FREE + Premium tiers)
    try:
        from .api.ocr_routes import ocr_bp as ocr_blueprint
        app.register_blueprint(ocr_blueprint)
        app.logger.info("✅ OCR service registered (FREE Tesseract + Premium Google Vision)")
    except Exception as e:
        app.logger.error(f"❌ Could not load OCR routes: {e}")
    
    # Expense Management (Scan receipts, track spending, optimize costs)
    try:
        from .api.expense_routes import expense_bp as expense_blueprint
        app.register_blueprint(expense_blueprint)
        app.logger.info("✅ Expense management registered (Receipt scanning + Analytics)")
    except Exception as e:
        app.logger.error(f"❌ Could not load expense routes: {e}")
    
    # Batch Processing (100+ documents at once)
    try:
        from .api.batch_processing_routes import batch_bp as batch_blueprint
        app.register_blueprint(batch_blueprint)
        app.logger.info("✅ Batch processing registered (Mass document scanning)")
    except Exception as e:
        app.logger.error(f"❌ Could not load batch processing routes: {e}")
    
    # Diagnostics (Ferrari inspection tool)
    try:
        from .api.diagnostics import diagnostics as diagnostics_blueprint
        app.register_blueprint(diagnostics_blueprint)
        app.logger.info("✅ Ferrari diagnostics registered (System inspection)")
    except Exception as e:
        app.logger.error(f"❌ Could not load diagnostics: {e}")
    
    # System Check (Complete dependency verification)
    try:
        from .api.system_check import system_check as system_check_blueprint
        app.register_blueprint(system_check_blueprint)
        app.logger.info("✅ System check registered (Dependency verification)")
    except Exception as e:
        app.logger.error(f"❌ Could not load system check: {e}")
    
    # Working Tests (Simple endpoints guaranteed to work)
    try:
        from .api.working_tests import working as working_blueprint
        app.register_blueprint(working_blueprint)
        app.logger.info("✅ Working test endpoints registered (SIMPLE TESTS)")
    except Exception as e:
        app.logger.error(f"❌ Could not load working tests: {e}")
    
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
        from .api.funding_routes import funding as funding_blueprint
        app.register_blueprint(funding_blueprint)
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
    
    # API-only root route (frontend will be on Vercel)
    @app.route('/')
    def root():
        """API root - Frontend is deployed separately on Vercel"""
        return jsonify({
            'name': 'CLARITY Engine API',
            'version': '5.0',
            'status': 'live',
            'features': {
                'multi_llm_router': True,
                'funding_readiness_engine': True,
                'outstanding_writing_system': True,
                'api_management': True,
                'auth': True,
            },
            'frontend_url': 'https://clarity-frontend.vercel.app',
            'api_docs': '/api/docs',
            'health': '/health'
        })
    
    # --- Health Check ---
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'mode': 'production', 'service': 'backend-api'})
    
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
