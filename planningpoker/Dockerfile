FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PORT=8080 \
    GOOGLE_CLOUD_PROJECT=effortpoker

WORKDIR /app

# Dependencies zuerst kopieren und installieren (nutzt Docker Layer-Caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY . .

EXPOSE 8080

# Multi-threaded Gunicorn für langlebige SSE-Streams und hohe Concurrency
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 128 --timeout 0 --forwarded-allow-ips='*' main:app
