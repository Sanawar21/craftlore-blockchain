FROM python:3.6-slim
WORKDIR /project

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the transaction processor code
COPY . .


# Set the entrypoint
ENTRYPOINT ["python3", "processor.py"]