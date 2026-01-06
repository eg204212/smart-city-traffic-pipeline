FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir kafka-python

# Copy producer script
COPY traffic_producer.py .

# Run the producer
CMD ["python", "traffic_producer.py"]
