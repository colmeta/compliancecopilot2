
# app/main/routes.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
@login_required # This is the crucial part: this page is now protected.
def index():
    """This will be the user's dashboard after they log in."""
    return f"<h1>Welcome to the Clarity Engine, {current_user.email}!</h1> You are now logged in."
