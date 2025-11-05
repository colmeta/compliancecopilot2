#!/bin/bash
set -o errexit

echo "🚀 CLARITY Engine - Render Build Script"
echo "========================================"

# Check Python version
python --version

echo "📦 Installing Python Dependencies..."
# Use minimal requirements first to ensure build succeeds
if [ -f "requirements-render-minimal.txt" ]; then
    echo "Using requirements-render-minimal.txt (minimal for guaranteed build)"
    pip install --upgrade pip
    pip install -r requirements-render-minimal.txt
elif [ -f "requirements-render.txt" ]; then
    echo "Using requirements-render.txt (optimized for Render)"
    pip install --upgrade pip
    pip install -r requirements-render.txt
else
    echo "Using requirements.txt"
    pip install --upgrade pip
    pip install -r requirements.txt
fi

echo "🗄️ Running Database Migrations..."
export FLASK_APP=run.py

# Render provides DATABASE_URL automatically
if [ -n "$DATABASE_URL" ]; then
    echo "✅ DATABASE_URL detected"
    flask db upgrade
else
    echo "⚠️ DATABASE_URL not set - skipping migrations"
fi

echo "🔍 Running Health Checks..."
# Test imports (lightweight check)
python -c "
import sys
try:
    from app import create_app
    print('✅ App imports successful')
except Exception as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"

# Test database only if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
    python -c "
import sys
try:
    from app import create_app, db
    from sqlalchemy import text
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            conn.execute(text('SELECT 1'))
    print('✅ Database connection successful')
except Exception as e:
    print(f'⚠️ Database check failed: {e}')
    print('This may be normal if database is not yet provisioned')
    # Don\'t exit - let the app start and retry
"
fi

echo "🎉 Build Complete - CLARITY Engine is ready!"
echo "============================================"
