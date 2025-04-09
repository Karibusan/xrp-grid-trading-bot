FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/src/
COPY scripts/ /app/scripts/

# Create necessary directories
RUN mkdir -p /app/config /app/data /app/logs /app/backups

# Make scripts executable
RUN chmod +x /app/scripts/*.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "src/main.py"]
