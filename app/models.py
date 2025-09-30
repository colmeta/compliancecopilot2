# ==============================================================================
# app/models.py -- CORRECTED
# This file now IMPORTS the central db object instead of creating a new one.
# ==============================================================================

# Import the ONE TRUE db instance from our app factory package
from . import db

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    # ... your User class code remains IDENTICAL ...
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # ... and so on ...
