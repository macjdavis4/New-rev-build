FROM python:3.10-slim

LABEL maintainer="Revenue Builder Team <info@revenue-builder.com>"
LABEL description="ML-Powered Revenue Forecasting System"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY revenue_builder/ ./revenue_builder/
COPY setup.py .
COPY README.md .

# Install package
RUN pip install -e .

# Expose API port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=revenue_builder.api.rest_api
ENV PYTHONUNBUFFERED=1

# Run API server
CMD ["python", "-m", "revenue_builder.api.rest_api"]
