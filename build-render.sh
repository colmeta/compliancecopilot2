#!/bin/bash
# EXTREME MINIMAL BUILD SCRIPT FOR DEBUG

echo "🚀 Starting build..."

# Install deps
pip install --upgrade pip
pip install -r requirements-render-test.txt

echo "✅ Build complete"
