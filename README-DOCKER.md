# NVIDIA RTX 5090 Stock Checker - Docker/Unraid Guide

Run the stock checker 24/7 on your Unraid server (or any Docker host) without keeping your PC on!

## Features in Docker Mode

✅ **Works:**
- 📱 Telegram notifications to your phone
- 📧 Email notifications and health checks
- 🍪 Session persistence (cookies)
- 🔄 Auto-restart on crashes
- 📊 Full logging and screenshots
- 🌐 Best Buy + NVIDIA monitoring

❌ **Doesn't Work:**
- 🔊 PC sound alerts (no audio in headless container)
- 💤 Keep-awake (not needed - containers don't sleep)

## Quick Start for Unraid

### Step 1: Download the Project

SSH into your Unraid server or use the terminal:

```bash
cd /mnt/user/appdata
git clone https://github.com/curtisjmorrow/NvidiaWebsite5090Checker.git
cd NvidiaWebsite5090Checker
```

### Step 2: Create Notification Config

```bash
# Create the config file
python3 nvidia_stock_checker.py --create-notify-config

# Edit it with your details
nano notification_config.json
```

**Minimal Telegram setup** (see main README for detailed Telegram setup):
```json
{
  "email": {
    "enabled": false
  },
  "telegram": {
    "enabled": true,
    "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
    "chat_id": "987654321"
  },
  "desktop": {
    "enabled": false
  },
  "sound": {
    "enabled": false
  }
}
```

**With email health checks** (recommended):
```json
{
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "curtisjmorrow@gmail.com",
    "sender_password": "your-16-char-app-password",
    "recipient_email": "curtisjmorrow@gmail.com"
  },
  "telegram": {
    "enabled": true,
    "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
    "chat_id": "987654321"
  },
  "desktop": {
    "enabled": false
  },
  "sound": {
    "enabled": false
  }
}
```

### Step 3: Set Your Timezone (Optional)

Edit `docker-compose.yml` and change the timezone:

```yaml
environment:
  - TZ=America/New_York  # Change to your timezone
```

Common timezones:
- `America/New_York` (Eastern)
- `America/Chicago` (Central)
- `America/Denver` (Mountain)
- `America/Los_Angeles` (Pacific)
- `Europe/London`
- Full list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

### Step 4: Start the Container

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

You should see:
```
INFO - Starting stock monitoring (base interval: 10s with randomization)
INFO - Monitoring 2 URL(s)
INFO - Daily health checks enabled (every 24 hours via email)
INFO - Preventing PC from sleeping during monitoring
INFO - Chrome WebDriver initialized successfully
```

### Step 5: Verify It's Working

Watch the logs for a minute:
```bash
docker-compose logs -f
```

You should see:
- `Check #1`, `Check #2`, etc.
- `NVIDIA: Out of stock - ...`
- `Best Buy: Out of stock - ...`

Press `Ctrl+C` to exit log view (container keeps running).

## Managing the Container

### View Logs
```bash
# Live tail
docker-compose logs -f

# Last 50 lines
docker-compose logs --tail=50

# Search logs
docker-compose logs | grep "IN STOCK"
```

### Stop/Start/Restart
```bash
# Stop
docker-compose stop

# Start
docker-compose start

# Restart
docker-compose restart

# Stop and remove (keeps data)
docker-compose down
```

### Update to Latest Version
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Check Resource Usage
```bash
docker stats nvidia-5090-checker
```

## Customization

### Change Check Interval

Edit `docker-compose.yml`:
```yaml
environment:
  - CHECK_INTERVAL=30  # Check every 30 seconds instead of 10
```

Then restart:
```bash
docker-compose up -d
```

### Change Health Check Frequency

Edit `docker-compose.yml`:
```yaml
environment:
  - HEALTH_CHECK_HOURS=12  # Email every 12 hours instead of 24
```

### Monitor Only NVIDIA or Only Best Buy

Edit `docker-compose.yml` CMD section at the bottom of `Dockerfile`:

**Only NVIDIA:**
```dockerfile
CMD ["sh", "-c", "python -u nvidia_stock_checker.py \
    --monitor \
    --no-bestbuy \
    --interval ${CHECK_INTERVAL} \
    --health-check-hours ${HEALTH_CHECK_HOURS} \
    --notify-config /app/data/notification_config.json"]
```

**Only Best Buy:**
```dockerfile
CMD ["sh", "-c", "python -u nvidia_stock_checker.py \
    --monitor \
    --no-nvidia \
    --interval ${CHECK_INTERVAL} \
    --health-check-hours ${HEALTH_CHECK_HOURS} \
    --notify-config /app/data/notification_config.json"]
```

Then rebuild:
```bash
docker-compose up -d --build
```

### Custom Best Buy URL

If Best Buy changes their URL again:

```dockerfile
CMD ["sh", "-c", "python -u nvidia_stock_checker.py \
    --monitor \
    --bestbuy-url 'https://www.bestbuy.com/product/...' \
    --interval ${CHECK_INTERVAL} \
    --health-check-hours ${HEALTH_CHECK_HOURS} \
    --notify-config /app/data/notification_config.json"]
```

## File Locations

All persistent data is stored in `./docker-data/`:

```
/mnt/user/appdata/NvidiaWebsite5090Checker/
├── notification_config.json         # Your config (mounted read-only)
├── docker-data/
│   ├── cookies/
│   │   └── browser_cookies.pkl      # Session persistence
│   ├── logs/
│   │   └── stock_checker.log        # Log file
│   └── screenshots/
│       └── screenshot_*.png         # Debug screenshots
```

### View Logs from Unraid
```bash
cat /mnt/user/appdata/NvidiaWebsite5090Checker/docker-data/logs/stock_checker.log
```

### View Screenshots
Navigate to `/mnt/user/appdata/NvidiaWebsite5090Checker/docker-data/screenshots/` in the Unraid file browser.

## Auto-Start on Unraid Boot

The container is configured with `restart: unless-stopped`, so it will automatically start when Unraid boots.

To manually control auto-start:

```bash
# Disable auto-start
docker update --restart=no nvidia-5090-checker

# Enable auto-start
docker update --restart=unless-stopped nvidia-5090-checker
```

## Troubleshooting

### Container Keeps Restarting

Check logs:
```bash
docker-compose logs --tail=100
```

Common issues:
- **"notification_config.json not found"** - Make sure you created it in the root directory
- **"Failed to initialize Chrome WebDriver"** - Rebuild: `docker-compose up -d --build`
- **"Telegram config incomplete"** - Check your bot token and chat ID in config

### No Notifications Received

```bash
# Test notifications from inside container
docker-compose exec nvidia-stock-checker python nvidia_stock_checker.py --test-notification
```

If test fails:
- Check Telegram bot token and chat ID
- Verify you messaged the bot first (`/start`)
- Check email credentials if using email

### High CPU/Memory Usage

View stats:
```bash
docker stats nvidia-5090-checker
```

Normal usage:
- **CPU**: 5-15% during checks, ~0% idle
- **Memory**: 200-400 MB

If higher:
- Check interval (10s is aggressive, consider 30s)
- Check for errors in logs causing retries

### Container Not Starting

```bash
# Check Docker daemon
systemctl status docker

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Performance Tuning

### Resource Limits

Default limits in `docker-compose.yml`:
- CPU: 1 core max, 0.25 cores reserved
- Memory: 1GB max, 256MB reserved

To change:
```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'      # Lower for less powerful servers
      memory: 512M
```

### Reduce Logging

If logs are too verbose, edit Dockerfile:
```dockerfile
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=WARNING  # Only warnings and errors
```

## Unraid Community Applications Template

Want to install via Unraid GUI? Create this template:

1. Go to Docker tab → Add Container
2. Fill in:
   - **Name**: `nvidia-5090-checker`
   - **Repository**: `curtisjmorrow/nvidia-5090-checker:latest` (after you publish to Docker Hub)
   - **Path**: `/app/data` → `/mnt/user/appdata/nvidia-5090-checker`
   - **Path**: `/app/logs` → `/mnt/user/appdata/nvidia-5090-checker/logs`
   - **Variable**: `CHECK_INTERVAL` = `10`
   - **Variable**: `HEALTH_CHECK_HOURS` = `24`
   - **Variable**: `TZ` = `America/New_York`

## Advanced: Publishing to Docker Hub

To make installation even easier:

```bash
# Build for your architecture
docker build -t curtisjmorrow/nvidia-5090-checker:latest .

# Login to Docker Hub
docker login

# Push
docker push curtisjmorrow/nvidia-5090-checker:latest
```

Then you (and others) can install with:
```yaml
services:
  nvidia-stock-checker:
    image: curtisjmorrow/nvidia-5090-checker:latest  # No build needed!
    # ... rest of config
```

## Support

- Main README: [README.md](README.md)
- Telegram setup: See main README Step 4
- Gmail app password: See main README "Optional: Set Up Email Health Checks"
- Issues: https://github.com/curtisjmorrow/NvidiaWebsite5090Checker/issues

## Benefits of Docker vs Windows

| Feature | Windows | Docker/Unraid |
|---------|---------|---------------|
| **Always on** | PC must stay on | Server runs 24/7 |
| **Power usage** | ~100-300W | Server already running |
| **Updates** | Manual git pull | `docker-compose up -d --build` |
| **Logs** | Local file only | Persistent, can view remotely |
| **Crashes** | Manual restart | Auto-restart |
| **Telegram** | ✅ | ✅ |
| **Email** | ✅ | ✅ |
| **PC Sound** | ✅ | ❌ (no audio) |
| **Keep Awake** | Needed | Not needed |

Docker is ideal for set-and-forget 24/7 monitoring!
