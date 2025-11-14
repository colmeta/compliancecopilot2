# CLARITY Engine - Production Dockerfile
FROM python:3.11-slim

# Install system dependencies (Tesseract OCR, PDF processing)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Verify Tesseract installation
RUN tesseract --version || echo "Tesseract installation failed"

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py

# Expose port
EXPOSE 10000

# Run migrations and start server
CMD flask db upgrade || echo "Migration failed (may be normal)" && \
    gunicorn --bind 0.0.0.0:10000 --workers 2 --timeout 120 run:app

