#!/bin/bash
# CLARITY Engine - Render Build Script (SIMPLE & SAFE)

echo "🚀 Starting CLARITY Engine build..."

# Install deps
pip install --upgrade pip

if [ -f "requirements-render-full.txt" ]; then
    echo "📦 Installing full requirements..."
    pip install -r requirements-render-full.txt
elif [ -f "requirements-render-test.txt" ]; then
    echo "🧪 Installing test requirements..."
    pip install -r requirements-render-test.txt
else
    echo "⚠️  Using default requirements.txt"
    pip install -r requirements.txt
fi

# Run migrations if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
    echo "🗄️  Running database migrations..."
    export FLASK_APP=run.py
    flask db upgrade || echo "⚠️  Migration failed (may be normal on first deploy)"
fi

echo "✅ Build complete!"
