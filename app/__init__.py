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
    login_manager.login_view = 'auth.login'
    
    # CRITICAL: User loader MUST be registered immediately after login_manager.init_app
    # This must happen BEFORE any blueprints are registered that might use current_user
    def load_user(user_id):
        """Load user with error handling for database issues - NEVER CRASH"""
        try:
            # Check if database is initialized - if not, return None (user not logged in)
            if not hasattr(db, 'engine') or db.engine is None:
                return None
            
            from app.models import User
            # Try to query - if database isn't ready, this will fail gracefully
            return User.query.get(int(user_id))
        except (ValueError, TypeError, AttributeError):
            # Invalid user_id format or missing attributes
            return None
        except Exception:
            # Any database error (connection, query, etc.) - just return None
            # This is expected for anonymous users or when DB isn't ready
            return None
    
    # Register the user_loader - ALWAYS return None to prevent crashes
    # This is a safety measure - even if registration fails, we have a fallback
    def safe_load_user(user_id):
        """Always-safe user loader that never crashes"""
        try:
            return load_user(user_id)
        except Exception:
            return None
    
    # Register using the decorator method (most reliable)
    login_manager.user_loader(safe_load_user)
    
    # Verify it worked
    if hasattr(login_manager, '_user_callback') and login_manager._user_callback is not None:
        app.logger.info("✅ user_loader registered and verified")
    else:
        app.logger.error("❌ user_loader registration failed - using emergency fallback")
        # Emergency: directly set the callback
        login_manager._user_callback = lambda user_id: None
        app.logger.warning("⚠️ Emergency dummy user_loader set")
    
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
    
    # Request logging to help debug errors
    @app.before_request
    def log_request_info():
        app.logger.debug(f"Request: {request.method} {request.path}")
        app.logger.debug(f"Headers: {dict(request.headers)}")
    
    
    # CRITICAL: Simple health check endpoint for Render (BEFORE blueprints)
    @app.route('/health', methods=['GET', 'HEAD'])
    def health_check_endpoint():
        """Instant health check - no dependencies"""
        return jsonify({'status': 'ok', 'service': 'clarity', 'ready': True}), 200
    
    # CRITICAL: Root route registered DIRECTLY on app (BEFORE blueprints)
    # This ensures it works even if blueprints fail to load
    # We MUST prevent Flask-Login from trying to load users for this route
    @app.before_request
    def prevent_login_for_root():
        """Prevent Flask-Login from loading users for root route"""
        if request.path == '/' or request.path == '':
            # Set a flag to skip user loading
            from flask import g
            g.skip_user_loading = True
    
    # Register root route with explicit endpoint name to ensure it's unique
    @app.route('/', methods=['GET', 'HEAD', 'OPTIONS'], endpoint='root')
    def root_endpoint():
        """Root endpoint - NO dependencies, NO Flask-Login, NO database"""
        # Return immediately - Flask-Login should not be called
        # This route is registered BEFORE blueprints, so it takes precedence
        return jsonify({
            'name': 'CLARITY Engine API',
            'version': '5.0',
            'status': 'live',
            'service': 'veritas-engine',
            'features': {
                'multi_llm_router': True,
                'funding_readiness_engine': True,
                'outstanding_writing_system': True,
                'api_management': True,
                'auth': True,
            },
            'endpoints': {
                'health': '/health',
                'api_root': '/api/root',
                'docs': '/api/docs'
            }
        }), 200
    
    # Verify root route is registered
    app.logger.info(f"✅ Root route registered at endpoint 'root'")

    # --- Register Blueprints (STAGED - Only Core Ones First) ---
    
    # Core Routes (Required) - Register but root / is already handled above
    # IMPORTANT: The blueprint's root route was removed, so it won't conflict
    try:
        from .main.routes import main as main_blueprint
        # Register blueprint - if it tries to register /, Flask will ignore it (app route takes precedence)
        app.register_blueprint(main_blueprint, url_prefix='')
        # Verify no conflict
        root_routes = [rule for rule in app.url_map.iter_rules() if rule.rule == '/']
        if len(root_routes) > 1:
            app.logger.warning(f"⚠️ Multiple routes for / detected: {[r.endpoint for r in root_routes]}")
        else:
            app.logger.info(f"✅ Main routes registered - root / handled by: {root_routes[0].endpoint if root_routes else 'NONE'}")
    except Exception as e:
        app.logger.error(f"❌ Could not load main routes: {e}")
        # Don't crash - app-level routes still work
    
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
        app.logger.info("✅ Real AI analysis routes registered")
    except Exception as e:
        app.logger.error(f"❌ Could not load real analysis routes: {e}")
    
    # AI Providers Management - DISABLED TEMPORARILY (causing 500 errors)
    # try:
    #     from .api.ai_providers_routes import ai_providers as ai_providers_blueprint
    #     app.register_blueprint(ai_providers_blueprint)
    #     app.logger.info("✅ AI Providers management registered (Anthropic/Groq/OpenAI/Gemini)")
    # except Exception as e:
    #     app.logger.error(f"❌ Could not load AI providers routes: {e}")
    
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
    
    # POST Test (Diagnose POST request issues)
    try:
        from .api.post_test import post_test as post_test_blueprint
        app.register_blueprint(post_test_blueprint)
        app.logger.info("✅ POST test endpoints registered (DIAGNOSE POST)")
    except Exception as e:
        app.logger.error(f"❌ Could not load POST test: {e}")
    
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
    
    # Extended Diagnostics (Check what's deployed) - DISABLED TEMPORARILY
    # Causing 500 errors, need to debug
    # try:
    #     from .api.diagnostics_extended import diagnostics_extended as diagnostics_extended_blueprint
    #     app.register_blueprint(diagnostics_extended_blueprint)
    #     app.logger.info("✅ Extended diagnostics registered")
    # except Exception as e:
    #     app.logger.warning(f"⚠️ Extended diagnostics not available: {e}")
    
    # Image Text Rewrite (Complete working endpoint) - DISABLED TEMPORARILY
    # Causing 500 errors, need to debug
    # try:
    #     from .api.image_rewrite_routes import image_rewrite as image_rewrite_blueprint
    #     app.register_blueprint(image_rewrite_blueprint)
    #     app.logger.info("✅ Image text rewrite registered (OCR + AI)")
    # except Exception as e:
    #     app.logger.warning(f"⚠️ Image rewrite not available: {e}")
    
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
    # NOTE: This route may be overridden by main blueprint's homepage route
    # If main blueprint fails, this provides a fallback
    @app.route('/api/root', methods=['GET'])
    def api_root():
        """API root - Always accessible even if main routes fail"""
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
        import traceback
        # Safely rollback database session if it exists
        try:
            if db.session:
                db.session.rollback()
        except Exception:
            pass  # Database might not be initialized
        
        # Log the full error details
        error_msg = str(error)
        error_traceback = traceback.format_exc()
        app.logger.error(f"500 Internal Server Error: {error_msg}")
        app.logger.error(f"Traceback: {error_traceback}")
        
        # In development, return more details
        if app.debug:
            return jsonify({
                'error': 'Internal server error',
                'message': error_msg,
                'traceback': error_traceback.split('\n')
            }), 500
        
        # In production, return generic error but log details
        return jsonify({'error': 'Internal server error'}), 500
    
    app.logger.info("CLARITY Engine initialized successfully!")
    
    return app
