#!/bin/bash

# --- Automated Construction Script for Web-Based Deployment ---

# Exit immediately if a command exits with a non-zero status.
set -o errexit

echo "--- Installing Python Dependencies ---"
pip install -r requirements.txt

echo "--- Running Database Migrations ---"
# Set the FLASK_APP environment variable for this script's session
export FLASK_APP=run.py

# This is where the magic happens.
# This runs the same 'flask db upgrade' command you would have run locally.
# It reads your models.py blueprint and builds the tables in your database.
flask db upgrade

echo "--- Build Complete ---"
