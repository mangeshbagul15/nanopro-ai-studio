FROM python:3.11-slim

# Configure Hugging Face Spaces non-root user (UID 1000)
RUN useradd -m -u 1000 user

WORKDIR /home/user/app

# Install essential system dependencies (ffmpeg, sqlite3, curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Switch to user environment
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PORT=7860

# Install Python requirements
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application codebase and assets
COPY --chown=user:user . .

# Ensure runtime directories have write permissions
RUN mkdir -p app/logs app/database app/backups app/reports app/memory && \
    chmod -R 775 /home/user/app

# Hugging Face default port
EXPOSE 7860

# Start Mangesh Nano Pro AI Studio
CMD ["python", "main.py"]
