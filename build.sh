#!/bin/bash
set -o errexit

echo "--- Installing Python Dependencies ---"
pip install -r requirements.txt

echo "--- Running Database Migrations ---"
export FLASK_APP=run.py
# Use the DIRECT connection for migrating the database
SQLALCHEMY_DATABASE_URI=$DIRECT_URL flask db upgrade

echo "--- Build Complete ---"
