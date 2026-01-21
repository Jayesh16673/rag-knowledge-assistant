FROM python:3.10-slim

# Create non-root user for security
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install system dependencies - minimal
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies (no cache, strip bytecode)
RUN pip install --no-cache-dir --no-compile -r requirements.txt && \
    find /usr/local -name "*.pyc" -delete && \
    find /usr/local -name "__pycache__" -delete

# Copy entire project
COPY . .

# Remove unnecessary files to save space
RUN rm -rf .git .github *.md scripts tests .pytest_cache .mypy_cache

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Create cache directory for answer caching
RUN mkdir -p /app/cache && chown -R appuser:appuser /app/cache

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Run the app with single worker for 512MB
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
