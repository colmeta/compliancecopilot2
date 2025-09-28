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
