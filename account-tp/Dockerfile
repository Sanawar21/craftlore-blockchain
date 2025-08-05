FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (if needed for health checks)
EXPOSE 4004

# Set the entrypoint with proper arguments
# ENTRYPOINT ["python3", "processor.py", "-C", "tcp://validator:4004", "-vv"]
