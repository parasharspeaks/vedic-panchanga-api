# Use official Python base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies required by swisseph and others
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    gcc \
    && apt-get clean

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files to container
COPY . .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
