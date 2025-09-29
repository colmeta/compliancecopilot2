# =======================================================
# app/main/routes.py -- CORRECTED & FINAL VERSION
# =======================================================
from flask import Blueprint, render_template
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def homepage():
    """This is the PUBLIC landing page for the entire service."""
    return "<h1>Welcome to the Pearl AI Clarity Engine.</h1><p>Please <a href='/auth/login'>login</a> or <a href='/auth/register'>register</a> to continue.</p>"

@main.route('/dashboard')
@login_required
def dashboard():
    """This will be the user's dashboard after they log in."""
    return f"<h1>Clarity Engine Dashboard</h1><h2>Welcome, {current_user.email}!</h2><p><a href='/auth/logout'>Logout</a></p>"
