# Use lightweight official python image
FROM python:3.11-slim

# Install any required system packages (optional)
RUN apt-get update && apt-get install -y gcc build-essential && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy requirements first, install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your full code into container
COPY . .

# Expose port 8080 (Render default)
EXPOSE 8080

# Start uvicorn directly
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
