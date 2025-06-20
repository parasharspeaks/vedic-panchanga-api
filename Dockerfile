# Base image with Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install required system dependencies
RUN apt-get update && \
    apt-get install -y gcc libffi-dev libatlas-base-dev build-essential curl git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port
EXPOSE 10000

# Run the API server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
