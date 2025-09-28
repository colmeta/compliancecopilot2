# ==============================================================================
# app/main/routes.py
# COMPLETE FILE with the temporary setup route included.
# ==============================================================================
from flask import Blueprint, render_template
from flask_login import login_required, current_user

# Imports needed for our setup route
from app import db
from app.models import User, APIKey

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
@login_required
def index():
    """This will be the user's dashboard after they log in."""
    return f"<h1>Welcome to the Clarity Engine, {current_user.email}!</h1> You are now logged in."


# ==============================================================================
# !! TEMPORARY ADMIN SETUP ROUTE !!
# This is a temporary, secret endpoint to create the first user and API key.
# AFTER YOU USE THIS ONCE, YOU MUST DELETE THIS ENTIRE BLOCK OF CODE.
# ==============================================================================
@main.route('/setup/aBc123XyZ_INITIALIZE_FOUNDER_ACCOUNT')
def setup_initial_user():
    """
    Creates the first admin user and their API key.
    This is a one-time use endpoint and should be deleted after running.
    """
    # --- The Safety Latch ---
    if User.query.filter_by(email="founder@clarityengine.com").first():
        return "<h1>Setup Error</h1><p>The founder account already exists. This setup can only be run once. You should delete this code block from app/main/routes.py now.</p>", 400

    try:
        # --- The User Creation Logic ---
        print("--- Running Initial User Setup ---")
        user = User(email="founder@clarityengine.com", password="a_very_secure_password_change_this")
        db.session.add(user)
        db.session.commit()
        print(f"Successfully created user: {user.email}")
        
        # --- The API Key Generation Logic ---
        new_key_str, hashed_key = APIKey.generate_key()
        new_api_key = APIKey(user_id=user.id)
        new_api_key.key_hash = hashed_key
        db.session.add(new_api_key)
        db.session.commit()
        print(f"Successfully generated API key for {user.email}")
        
        # --- The Critical Output ---
        return f"""
        <h1>Fortress Setup Complete!</h1>
        <p>The first user and API key have been successfully generated.</p>
        <p><b>User Email:</b> {user.email}</p>
        <br>
        <h2>CRITICAL: Your API Key is Below.</h2>
        <p>Copy this key and save it in a secure location. It will NOT be shown again.</p>
        <p style="background-color: #f0f0f0; border: 1px solid #ccc; padding: 10px; font-family: monospace; font-size: 16px;">
            <b>{new_key_str}</b>
        </p>
        <br>
        <hr>
        <h3>Next Step: DELETE THIS ENDPOINT</h3>
        <p>For security, you must now go back to the app/main/routes.py file and DELETE this entire '@main.route('/setup/...')' code block, then redeploy the application.</p>
        """

    except Exception as e:
        return f"<h1>An Error Occurred</h1><p>Could not complete setup: {e}</p>", 500
