#!/bin/bash
set -o errexit

echo "🚀 CLARITY Engine Build Script"
echo "================================"

# Check if required environment variables are set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable is not set"
    exit 1
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ ERROR: GOOGLE_API_KEY environment variable is not set"
    exit 1
fi

if [ -z "$CELERY_BROKER_URL" ]; then
    echo "❌ ERROR: CELERY_BROKER_URL environment variable is not set"
    exit 1
fi

echo "✅ Environment variables validated"

echo "📦 Installing System Dependencies (OCR, PDF processing)..."
# Install Tesseract OCR (FREE - no credit card needed!)
# Render uses Ubuntu and we have apt permissions in build phase
echo "Installing tesseract-ocr..."
apt-get update -qq || echo "⚠️  apt-get update failed, continuing..."
apt-get install -y tesseract-ocr tesseract-ocr-eng libtesseract-dev poppler-utils || echo "⚠️  Some packages failed to install"

# Verify installation
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract OCR installed successfully!"
    tesseract --version | head -1
else
    echo "❌ Tesseract installation FAILED - OCR will not work"
    echo "📋 Checking available package managers..."
    which apt-get || echo "No apt-get"
    which yum || echo "No yum" 
    which apk || echo "No apk"
fi

echo "📦 Installing Python Dependencies..."
pip install -r requirements.txt

echo "🗄️ Running Database Migrations..."
export FLASK_APP=run.py

# Use the DIRECT connection for migrating the database
if [ -n "$DIRECT_URL" ]; then
    echo "Using DIRECT_URL for migrations..."
    SQLALCHEMY_DATABASE_URI=$DIRECT_URL flask db upgrade
else
    echo "Using DATABASE_URL for migrations..."
    SQLALCHEMY_DATABASE_URI=$DATABASE_URL flask db upgrade
fi

echo "🔍 Running Health Checks..."
# Test database connectivity (SQLAlchemy 2.0 compatible)
python -c "
from app import create_app, db
from sqlalchemy import text
app = create_app()
with app.app_context():
    try:
        with db.engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print('✅ Database connection successful')
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        exit(1)
"

echo "🎉 Build Complete - CLARITY Engine is ready!"
echo "=============================================="
echo "Next steps:"
echo "1. Start Redis: redis-server"
echo "2. Start Celery worker: celery -A celery_worker.celery worker --loglevel=info"
echo "3. Start Flask app: python run.py"
echo "4. Access at: http://localhost:5000"
