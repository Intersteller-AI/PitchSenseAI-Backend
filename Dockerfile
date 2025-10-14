# Use the official lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for Google Cloud SDK and grpc)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables for Google credentials (Cloud Run will inject automatically if using Workload Identity)
ENV PYTHONUNBUFFERED=1 \
    PORT=8080

# Expose Cloud Run port
EXPOSE 8080

# Run the app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
