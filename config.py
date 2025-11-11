# ==============================================================================
# config.py
# This is the control panel for our application. It loads settings from
# the .env file and makes them available to the rest of the app.
# ==============================================================================

import os
from dotenv import load_dotenv

# Find the absolute path of the root directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))

# Load the .env file from the root directory
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration settings."""
    
    # --- CORE APP CONFIGURATION ---
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'you-will-never-guess'
    
    # --- DATABASE CONFIGURATION ---
    # This takes the DATABASE_URL from your .env file
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # This silences a deprecation warning
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- CELERY (BACKGROUND WORKER) CONFIGURATION ---
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
    
    # --- API KEYS ---
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    
    # --- SECURITY CONFIGURATION ---
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # --- EMAIL CONFIGURATION (CRITICAL FOR SCALABILITY) ---
    # Send all results via email to prevent browser timeouts and crashes
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@claritypearl.com')
    ENABLE_EMAIL_DELIVERY = os.environ.get('ENABLE_EMAIL_DELIVERY', 'true').lower() == 'true'
    
    # --- RATE LIMITING ---
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    
    # --- VECTOR STORE (INTELLIGENCE VAULT) CONFIGURATION ---
    CHROMA_HOST = os.environ.get('CHROMA_HOST', 'localhost')
    CHROMA_PORT = int(os.environ.get('CHROMA_PORT', '8000'))
    CHROMA_PERSIST_DIRECTORY = os.environ.get('CHROMA_PERSIST_DIRECTORY', './chroma_data')
    
    # Embedding Model Configuration
    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    EMBEDDING_DIMENSION = 384  # Dimension for all-MiniLM-L6-v2
    
    # Chunking Configuration
    CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', '1000'))  # Characters per chunk
    CHUNK_OVERLAP = int(os.environ.get('CHUNK_OVERLAP', '200'))  # Overlap between chunks
    
    # ==============================================================================
    # PHASE 4: ADVANCED FEATURES CONFIGURATION
    # ==============================================================================
    
    # --- Tier System ---
    DEFAULT_TIER = os.environ.get('DEFAULT_TIER', 'free')
    
    # --- Audio Transcription Services ---
    GOOGLE_SPEECH_API_KEY = os.environ.get('GOOGLE_SPEECH_API_KEY')
    ASSEMBLYAI_API_KEY = os.environ.get('ASSEMBLYAI_API_KEY')
    
    # --- Vision/OCR Services ---
    GOOGLE_VISION_API_KEY = os.environ.get('GOOGLE_VISION_API_KEY')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    
    # --- Model Routing ---
    ENABLE_MODEL_ROUTING = os.environ.get('ENABLE_MODEL_ROUTING', 'true').lower() == 'true'
    DEFAULT_MODEL = os.environ.get('DEFAULT_MODEL', 'gemini-1.5-flash')
    
    # Model routing configuration
    MODEL_ROUTING = {
        'simple': 'gemini-1.5-flash',
        'standard': 'gemini-1.5-pro',
        'complex': 'gemini-1.5-ultra',
        'multimodal': 'gemini-pro-vision'
    }
    
    # --- Caching ---
    ENABLE_RESPONSE_CACHE = os.environ.get('ENABLE_RESPONSE_CACHE', 'true').lower() == 'true'
    CACHE_TTL_SECONDS = int(os.environ.get('CACHE_TTL_SECONDS', '3600'))
    
    # --- Compliance & Security ---
    ENABLE_AUDIT_LOGGING = os.environ.get('ENABLE_AUDIT_LOGGING', 'true').lower() == 'true'
    DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS', '2555'))  # 7 years
    ENABLE_PII_DETECTION = os.environ.get('ENABLE_PII_DETECTION', 'true').lower() == 'true'
    
    # --- WebSocket (for collaboration) ---
    SOCKETIO_MESSAGE_QUEUE = os.environ.get('SOCKETIO_MESSAGE_QUEUE', 'redis://localhost:6379/2')
    
    # --- Advanced Chunking ---
    ENABLE_ADVANCED_CHUNKING = os.environ.get('ENABLE_ADVANCED_CHUNKING', 'true').lower() == 'true'
    DEFAULT_CHUNKING_STRATEGY = os.environ.get('DEFAULT_CHUNKING_STRATEGY', 'dynamic')
    
    # --- Multi-Modal Processing ---
    ENABLE_AUDIO_PROCESSING = os.environ.get('ENABLE_AUDIO_PROCESSING', 'true').lower() == 'true'
    ENABLE_VIDEO_PROCESSING = os.environ.get('ENABLE_VIDEO_PROCESSING', 'true').lower() == 'true'
    ENABLE_OCR_PROCESSING = os.environ.get('ENABLE_OCR_PROCESSING', 'true').lower() == 'true'
    
    # --- Analytics ---
    ENABLE_ANALYTICS = os.environ.get('ENABLE_ANALYTICS', 'true').lower() == 'true'
    ANALYTICS_RETENTION_DAYS = int(os.environ.get('ANALYTICS_RETENTION_DAYS', '365'))
    
    # --- Collaboration ---
    ENABLE_WORKSPACES = os.environ.get('ENABLE_WORKSPACES', 'true').lower() == 'true'
    ENABLE_REAL_TIME_COLLAB = os.environ.get('ENABLE_REAL_TIME_COLLAB', 'true').lower() == 'true'
    
    # ==============================================================================
    # PHASE 4E: AI MODEL OPTIMIZATION CONFIGURATION
    # ==============================================================================
    
    # AI Model Optimization
    ENABLE_AI_OPTIMIZATION = os.environ.get('ENABLE_AI_OPTIMIZATION', 'true').lower() == 'true'
    ENABLE_MODEL_ROUTING = os.environ.get('ENABLE_MODEL_ROUTING', 'true').lower() == 'true'
    ENABLE_RESPONSE_CACHING = os.environ.get('ENABLE_RESPONSE_CACHING', 'true').lower() == 'true'
    ENABLE_PROMPT_OPTIMIZATION = os.environ.get('ENABLE_PROMPT_OPTIMIZATION', 'true').lower() == 'true'
    ENABLE_COST_OPTIMIZATION = os.environ.get('ENABLE_COST_OPTIMIZATION', 'true').lower() == 'true'
    
    # Model Selection
    DEFAULT_MODEL_SELECTION_STRATEGY = os.environ.get('DEFAULT_MODEL_SELECTION_STRATEGY', 'cost_quality_balanced')
    MODEL_PERFORMANCE_TRACKING_ENABLED = os.environ.get('MODEL_PERFORMANCE_TRACKING_ENABLED', 'true').lower() == 'true'
    MODEL_SELECTION_CACHE_TTL = int(os.environ.get('MODEL_SELECTION_CACHE_TTL', '300'))  # 5 minutes
    
    # Response Caching
    CACHE_SIMILARITY_THRESHOLD = float(os.environ.get('CACHE_SIMILARITY_THRESHOLD', '0.85'))
    CACHE_EMBEDDING_MODEL = os.environ.get('CACHE_EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    CACHE_MAX_ENTRIES_PER_USER = int(os.environ.get('CACHE_MAX_ENTRIES_PER_USER', '1000'))
    CACHE_CLEANUP_INTERVAL_HOURS = int(os.environ.get('CACHE_CLEANUP_INTERVAL_HOURS', '24'))
    
    # Prompt Optimization
    PROMPT_AB_TESTING_ENABLED = os.environ.get('PROMPT_AB_TESTING_ENABLED', 'true').lower() == 'true'
    PROMPT_VARIANT_MIN_SAMPLES = int(os.environ.get('PROMPT_VARIANT_MIN_SAMPLES', '10'))
    PROMPT_VARIANT_MAX_SAMPLES = int(os.environ.get('PROMPT_VARIANT_MAX_SAMPLES', '1000'))
    PROMPT_OPTIMIZATION_CONFIDENCE_LEVEL = float(os.environ.get('PROMPT_OPTIMIZATION_CONFIDENCE_LEVEL', '0.95'))
    
    # Cost Optimization
    COST_TRACKING_ENABLED = os.environ.get('COST_TRACKING_ENABLED', 'true').lower() == 'true'
    COST_ANALYTICS_RETENTION_DAYS = int(os.environ.get('COST_ANALYTICS_RETENTION_DAYS', '90'))
    COST_ALERT_THRESHOLD_MONTHLY = float(os.environ.get('COST_ALERT_THRESHOLD_MONTHLY', '100.0'))
    COST_OPTIMIZATION_RECOMMENDATIONS_ENABLED = os.environ.get('COST_OPTIMIZATION_RECOMMENDATIONS_ENABLED', 'true').lower() == 'true'
    
    # Model Cost Configuration
    MODEL_COST_CONFIG = {
        'gemini-1.5-flash': {
            'input_cost_per_1k': 0.000075,
            'output_cost_per_1k': 0.0003,
            'tier': 'free'
        },
        'gemini-1.5-pro': {
            'input_cost_per_1k': 0.00125,
            'output_cost_per_1k': 0.005,
            'tier': 'pro'
        },
        'gemini-1.5-ultra': {
            'input_cost_per_1k': 0.0035,
            'output_cost_per_1k': 0.014,
            'tier': 'enterprise'
        },
        'gemini-pro-vision': {
            'input_cost_per_1k': 0.00125,
            'output_cost_per_1k': 0.005,
            'tier': 'pro'
        }
    }
    
    # Tier-based Cost Multipliers
    TIER_COST_MULTIPLIERS = {
        'free': 1.0,
        'pro': 0.8,
        'enterprise': 0.6
    }
    
    # Performance Tracking
    PERFORMANCE_METRICS_RETENTION_DAYS = int(os.environ.get('PERFORMANCE_METRICS_RETENTION_DAYS', '30'))
    PERFORMANCE_AGGREGATION_INTERVAL_HOURS = int(os.environ.get('PERFORMANCE_AGGREGATION_INTERVAL_HOURS', '1'))
    
    # A/B Testing
    AB_TESTING_MIN_DURATION_DAYS = int(os.environ.get('AB_TESTING_MIN_DURATION_DAYS', '7'))
    AB_TESTING_MAX_DURATION_DAYS = int(os.environ.get('AB_TESTING_MAX_DURATION_DAYS', '30'))
    AB_TESTING_SIGNIFICANCE_LEVEL = float(os.environ.get('AB_TESTING_SIGNIFICANCE_LEVEL', '0.05'))
    
    # Optimization Alerts
    ENABLE_OPTIMIZATION_ALERTS = os.environ.get('ENABLE_OPTIMIZATION_ALERTS', 'true').lower() == 'true'
    OPTIMIZATION_ALERT_EMAIL = os.environ.get('OPTIMIZATION_ALERT_EMAIL')
    OPTIMIZATION_ALERT_WEBHOOK_URL = os.environ.get('OPTIMIZATION_ALERT_WEBHOOK_URL')
    
    @staticmethod
    def validate_required_env_vars():
        """Validate that all required environment variables are set."""
        required_vars = [
            'DATABASE_URL',
            'GOOGLE_API_KEY', 
            'CELERY_BROKER_URL',
            'CELERY_RESULT_BACKEND'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True