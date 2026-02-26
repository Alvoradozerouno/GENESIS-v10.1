# GENESIS AI/ML Risk Engine - Container Image
FROM python:3.14-slim

LABEL maintainer="GENESIS Team"
LABEL description="AI/ML Risk Scoring Engine for EU Banking Compliance"
LABEL version="10.1"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY ../requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy AI engine code
COPY risk_ml.py /app/risk_ml.py
COPY __init__.py /app/__init__.py 2>/dev/null || touch /app/__init__.py

# Create output directory
RUN mkdir -p /app/output

# Run as non-root user
RUN useradd -m -u 1000 genesis && chown -R genesis:genesis /app
USER genesis

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import risk_ml; print('healthy')" || exit 1

# Default command
CMD ["python", "risk_ml.py"]
