FROM python:3.11-slim

WORKDIR /app

# system libs for swisseph & geopy
RUN apt-get update && \
    apt-get install -y gcc build-essential libffi-dev libgeos-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
