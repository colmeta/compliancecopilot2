# ==============================================================================
# app/models.py
# UPDATED with the APIKey model.
# ==============================================================================

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
import secrets  # For generating secure random keys

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # --- ADD THIS LINE ---
    # This creates a "link" to the APIKey model.
    # It allows us to easily see all keys belonging to a user (user.api_keys)
    api_keys = db.relationship('APIKey', backref='owner', lazy='dynamic')
    # --- END OF ADDITION ---

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

# --- ADD THIS ENTIRE NEW CLASS ---
class APIKey(db.Model):
    """The APIKey model for protecting service endpoints."""
    
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    key_hash = db.Column(db.String(256), unique=True, nullable=False)
    # The 'user_id' column links this key to a specific user.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def __init__(self, user_id):
        self.user_id = user_id
    
    def check_key(self, key_to_check):
        """Checks if a provided key matches the stored hash."""
        # Note: Since the key itself is random, we can store a hash for extra security,
        # but for simplicity and management, some systems store the key directly.
        # Hashing provides a layer of defense if the DB is compromised.
        # This implementation assumes we hash the keys.
        return check_password_hash(self.key_hash, key_to_check)
        
    @staticmethod
    def generate_key():
        """Generates a new, secure API key."""
        # Generates a new key and hashes it for storage
        new_key = secrets.token_urlsafe(32) # e.g., 'abc-123-xyz_...'
        hashed_key = generate_password_hash(new_key, method='pbkdf2:sha256')
        return new_key, hashed_key
# --- END OF ADDITION ---
