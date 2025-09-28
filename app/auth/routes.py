# ==============================================================================
# app/auth/routes.py
# This file contains the routes for user authentication (login, logout, register).
# ==============================================================================

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from .forms import LoginForm, RegistrationForm
from app.models import User

# A "Blueprint" is a way to organize a group of related routes.
# We create a blueprint named 'auth'.
auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle requests to the /register route."""
    # If the user is already logged in, redirect them to a main page.
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # We'll create a 'main' blueprint later

    form = RegistrationForm()
    if form.validate_on_submit():
        # Create a new user with the form data.
        user = User(email=form.email.data, password=form.password.data)
        # Add the new user to the database.
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        # After registration, redirect to the login page.
        return redirect(url_for('auth.login'))
        
    # If it's a GET request or the form is invalid, show the registration form.
    # We will need to create the HTML templates for this.
    return render_template('auth/register.html', title='Register', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle requests to the /login route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        # Look up the user by their email address.
        user = User.query.filter_by(email=form.email.data).first()
        # Check if the user exists and the password is correct.
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
        
        # If credentials are valid, log the user in.
        # This function from Flask-Login handles the session cookie.
        login_user(user)
        
        # Redirect to a protected page (or a 'next' page if specified).
        return redirect(url_for('main.index'))
        
    return render_template('auth/login.html', title='Sign In', form=form)


@auth.route('/logout')
def logout():
    """Handle requests to the /logout route."""
    logout_user() # This function from Flask-Login clears the session.
    return redirect(url_for('main.index'))
