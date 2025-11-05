# ==============================================================================
# app/__init__.py
# CLARITY Platform - Flask Application Factory - ULTRA MINIMAL FOR DEBUG
# ==============================================================================

from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize extensions
db = SQLAlchemy()

def create_app():
    """Application factory for CLARITY platform - MINIMAL MODE"""
    app = Flask(__name__)
    
    # Basic config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///test.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    @app.route('/')
    def home():
        return jsonify({
            'status': 'CLARITY Engine is ALIVE!',
            'mode': 'MINIMAL DEBUG BUILD',
            'version': '5.0-debug'
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'mode': 'minimal'})
    
    app.logger.info("CLARITY Engine startup (MINIMAL MODE)")
    
    return app
