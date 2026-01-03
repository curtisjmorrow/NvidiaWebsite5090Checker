# NVIDIA RTX 5090 Stock Checker - Docker Image
# Optimized for headless operation on Unraid/Docker servers

FROM python:3.11-slim

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1) \
    && CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}") \
    && wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver_linux64.zip

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
# Note: wakepy not needed in Docker (containers don't sleep)
# Note: requests needed for Telegram/email notifications
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir requests

# Copy application files
COPY nvidia_stock_checker.py .
COPY notifier.py .

# Create directories for persistent data
RUN mkdir -p /app/data /app/logs

# Environment variables with defaults
ENV PYTHONUNBUFFERED=1
ENV CHECK_INTERVAL=10
ENV HEALTH_CHECK_HOURS=24
ENV TZ=America/New_York

# Volumes for persistent data
VOLUME ["/app/data", "/app/logs"]

# Health check - verify script is running
HEALTHCHECK --interval=5m --timeout=10s --start-period=30s --retries=3 \
    CMD pgrep -f "nvidia_stock_checker.py" || exit 1

# Run the stock checker
# Configuration will be mounted from host at /app/data/notification_config.json
CMD ["sh", "-c", "python -u nvidia_stock_checker.py \
    --monitor \
    --interval ${CHECK_INTERVAL} \
    --health-check-hours ${HEALTH_CHECK_HOURS} \
    --notify-config /app/data/notification_config.json"]
