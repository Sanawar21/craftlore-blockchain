FROM python:3.8-slim

WORKDIR /project

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the transaction processor code
COPY . .

# Set the entrypoint with auto-restart capability
ENTRYPOINT ["python3", "watch.py", "python3", "processor.py", "-C", "tcp://validator:4004", "-vv"]
