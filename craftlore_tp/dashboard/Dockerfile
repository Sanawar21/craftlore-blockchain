FROM python:3.8-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash dashboard
RUN chown -R dashboard:dashboard /app
USER dashboard

EXPOSE 5000

CMD ["python", "app.py"]