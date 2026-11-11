FROM python:3.11-slim

WORKDIR /app

# Install essential system dependencies (ffmpeg, sqlite3, curl, git)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    sqlite3 \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

RUN git config --system --add safe.directory /app

ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    GIT_AUTHOR_NAME="NanoPro Agent" \
    GIT_AUTHOR_EMAIL="nanopro@localhost" \
    GIT_COMMITTER_NAME="NanoPro Agent" \
    GIT_COMMITTER_EMAIL="nanopro@localhost"

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application codebase and assets
COPY . .

# Ensure runtime directories exist
RUN mkdir -p app/logs app/database app/backups app/reports app/memory

EXPOSE 8000

# Start Mangesh Nano Pro AI Studio
CMD ["python", "main.py"]
