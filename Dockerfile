FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p data logs backups

# Copy source code
COPY src/ src/
COPY config/ config/
COPY scripts/ scripts/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set entrypoint
CMD ["python3", "src/main.py"]

# Label with version
LABEL version="3.0.2"
LABEL description="XRP Grid Trading Bot with advanced analysis modules and Pushover notifications"
LABEL maintainer="Karibusan"
