# Simple Dockerfile for the Payment Gateway API
FROM python:3.12-slim

# Prevents python from writing .pyc files to disc and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps for common DB drivers (keep minimal)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifest first for better caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Provide reasonable defaults; encourage overriding in production
ENV DATABASE_URL="postgresql://postgres:password@db:5432/payment_gateway"
ENV SECRET_KEY="CHANGE_ME"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
