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

# CELERY_BROKER_URL is optional - only warn if not set
if [ -z "$CELERY_BROKER_URL" ]; then
    echo "⚠️  WARNING: CELERY_BROKER_URL not set - Celery features will be disabled"
else
    echo "✅ CELERY_BROKER_URL configured"
fi

echo "✅ Environment variables validated"

echo "📦 Installing System Dependencies (OCR, PDF processing)..."

# Check if we have sudo (Render's build environment)
if command -v sudo &> /dev/null; then
    echo "Using sudo for system package installation..."
    SUDO="sudo"
else
    echo "Running without sudo..."
    SUDO=""
fi

# Try to install Tesseract
echo "Installing tesseract-ocr and dependencies..."
$SUDO apt-get update -qq 2>&1 | grep -v "^Get:" || true
$SUDO apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    poppler-utils \
    2>&1 | grep -E "(Setting up|done|Unpacking)" || true

# Verify Tesseract installation
echo ""
echo "📋 Verifying installations..."
if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -1)
    echo "✅ Tesseract: $TESSERACT_VERSION"
else
    echo "❌ Tesseract: NOT FOUND"
    echo "⚠️  OCR features will be limited"
fi

# Verify poppler (PDF processing)
if command -v pdfinfo &> /dev/null; then
    POPPLER_VERSION=$(pdfinfo -v 2>&1 | head -1)
    echo "✅ Poppler: $POPPLER_VERSION"
else
    echo "❌ Poppler: NOT FOUND"
fi

echo ""

echo "📦 Installing Python Dependencies..."
echo "Installing critical document dependencies first..."
pip install --no-cache-dir reportlab==4.0.7 python-pptx==0.6.23 markdown2==2.4.13 pytesseract==0.3.13 || echo "⚠️  Some dependencies failed"

echo "Installing remaining dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "📋 Verifying critical dependencies..."
python3 -c "import reportlab; print('✅ reportlab installed')" || echo "❌ reportlab FAILED"
python3 -c "import pptx; print('✅ python-pptx installed')" || echo "❌ python-pptx FAILED"
python3 -c "import markdown2; print('✅ markdown2 installed')" || echo "❌ markdown2 FAILED"
python3 -c "import pytesseract; print('✅ pytesseract installed')" || echo "❌ pytesseract FAILED"

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
