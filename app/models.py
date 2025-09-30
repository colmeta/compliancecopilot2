# ==============================================================================
# app/models.py -- The DEFINITIVE AND COMPLETE Version
# This version contains both the User and the APIKey models.
# ==============================================================================

# Imports the ONE TRUE db instance from our app factory package in __init__.py
from . import db

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
import secrets

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    api_keys = db.relationship('APIKey', backref='owner', lazy='dynamic')

    def __init__(self, email, password):
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class APIKey(db.Model):
    """The APIKey model for protecting service endpoints."""
    
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    key_hash = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def __init__(self, user_id):
        self.user_id = user_id
    
    def check_key(self, key_to_check):
        return check_password_hash(self.key_hash, key_to_check)
        
    @staticmethod
    def generate_key():
        new_key = secrets.token_urlsafe(32)
        hashed_key = generate_password_hash(new_key, method='pbkdf2:sha256')
        return new_key, hashed_key
