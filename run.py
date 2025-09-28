# run.py
from app import create_app, db # Make sure to import 'db'
from app.models import User, APIKey # And your models

app = create_app()

# --- ADD THIS ENTIRE BLOCK ---

@app.shell_context_processor
def make_shell_context():
    """Makes important objects available in the Flask shell."""
    return {'db': db, 'User': User, 'APIKey': APIKey}

@app.cli.command("create-user-key")
def create_user_key():
    """
    A command-line tool to create a user and their first API key.
    Run this command with: flask create-user-key
    """
    print("--- Clarity Engine: Admin Key Generation ---")
    
    # 1. Create the User
    # For a real app, you would take email/password as input. Here we use defaults.
    email = "founder@clarityengine.com"
    password = "a_very_secure_password_change_this" # You should change this
    
    # Check if the user already exists
    if User.query.filter_by(email=email).first():
        print(f"User '{email}' already exists. Aborting.")
        return

    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()
    print(f"Successfully created user: {user.email}")
    
    # 2. Generate the API Key
    new_key_str, hashed_key = APIKey.generate_key()
    
    new_api_key = APIKey(user_id=user.id)
    new_api_key.key_hash = hashed_key
    
    db.session.add(new_api_key)
    db.session.commit()
    
    print("\n--- API KEY GENERATED SUCCESSFULLY ---")
    print("This key is shown only once. Store it securely.")
    print(f"User: {user.email}")
    print(f"API Key: {new_key_str}")
    print("\nUse this key in the 'X-API-KEY' header of your requests.")
    
# --- END OF BLOCK ---

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
