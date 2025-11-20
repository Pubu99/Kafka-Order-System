FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY kafka_project/ ./kafka_project/

# Default command (can be overridden)
CMD ["python", "kafka_project/consumer/consumer.py"]
