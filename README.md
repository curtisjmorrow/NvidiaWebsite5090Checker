# NVIDIA RTX 5090 Stock Checker

A Python script that automatically monitors the NVIDIA Marketplace for RTX 5090 Founders Edition stock availability and sends notifications when the card becomes available.

## Features

- Automated stock checking using Selenium WebDriver
- Multiple notification methods (email, desktop, Telegram, Discord, webhooks)
- Continuous monitoring mode for unattended operation
- Detailed logging to file and console
- Screenshot capture for debugging
- Multiple detection methods for stock status
- Configurable check intervals
- Headless or visible browser modes

## Requirements

- Python 3.7 or higher
- Chrome/Chromium browser
- ChromeDriver (matching your Chrome version)

## Installation

### 1. Install ChromeDriver

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install chromium-chromedriver
```

**macOS (with Homebrew):**
```bash
brew install chromedriver
```

**Windows:**
Download from [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads) and add to PATH.

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

For additional notification features, uncomment and install optional dependencies in `requirements.txt`:
```bash
# For desktop notifications
pip install plyer

# For Telegram/Discord/Webhook notifications
pip install requests
```

## Quick Start

### Single Check
Check stock once and exit:
```bash
python nvidia_stock_checker.py
```

### Continuous Monitoring
Monitor continuously (checks every 5 minutes by default):
```bash
python nvidia_stock_checker.py --monitor
```

### Custom Check Interval
Monitor with custom interval (e.g., every 2 minutes = 120 seconds):
```bash
python nvidia_stock_checker.py --monitor --interval 120
```

### Visible Browser Mode
Run with visible browser window (useful for debugging):
```bash
python nvidia_stock_checker.py --monitor --no-headless
```

## Notification Setup

### 1. Create Notification Configuration
```bash
python nvidia_stock_checker.py --create-notify-config
```

This creates a `notification_config.json` file with sample settings.

### 2. Edit Configuration

Edit `notification_config.json` to enable and configure your preferred notification methods:

#### Email Notifications
```json
{
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-app-password",
    "recipient_email": "recipient@example.com"
  }
}
```

**Gmail Setup:**
1. Enable 2-factor authentication on your Google account
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Use the app password in the configuration

#### Desktop Notifications
```json
{
  "desktop": {
    "enabled": true
  }
}
```

Requires `plyer` package (uncomment in `requirements.txt`).

#### Telegram Notifications
```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "your-bot-token",
    "chat_id": "your-chat-id"
  }
}
```

**Setup:**
1. Create a bot with [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Start a chat with your bot
4. Get your chat ID from `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`

#### Discord Notifications
```json
{
  "discord": {
    "enabled": true,
    "webhook_url": "https://discord.com/api/webhooks/..."
  }
}
```

**Setup:**
1. Go to Server Settings > Integrations > Webhooks
2. Create a new webhook
3. Copy the webhook URL

#### Sound Alerts
```json
{
  "sound": {
    "enabled": true,
    "file": "/path/to/custom/sound.mp3"
  }
}
```

Leave `file` empty to use system beep.

## Usage Examples

### Monitor for 1 hour with 3-minute intervals
```bash
python nvidia_stock_checker.py --monitor --interval 180 --duration 3600
```

### Check different product URL
```bash
python nvidia_stock_checker.py --url "https://marketplace.nvidia.com/en-us/..." --monitor
```

### Run in background (Linux/macOS)
```bash
nohup python nvidia_stock_checker.py --monitor > output.log 2>&1 &
```

### Run with systemd (Linux - persistent service)

Create `/etc/systemd/system/nvidia-stock-checker.service`:
```ini
[Unit]
Description=NVIDIA RTX 5090 Stock Checker
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/NvidiaWebsite5090Checker
ExecStart=/usr/bin/python3 nvidia_stock_checker.py --monitor --interval 300
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable nvidia-stock-checker
sudo systemctl start nvidia-stock-checker
```

Check status:
```bash
sudo systemctl status nvidia-stock-checker
sudo journalctl -u nvidia-stock-checker -f
```

### Run with screen (Linux - survive logout)
```bash
screen -S nvidia-checker
python nvidia_stock_checker.py --monitor
# Press Ctrl+A, then D to detach
# Reattach with: screen -r nvidia-checker
```

### Run with Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., "At startup")
4. Action: Start a program
   - Program: `python.exe`
   - Arguments: `C:\path\to\nvidia_stock_checker.py --monitor`
   - Start in: `C:\path\to\NvidiaWebsite5090Checker`

## Command-Line Options

```
usage: nvidia_stock_checker.py [-h] [--url URL] [--monitor] [--interval INTERVAL]
                               [--duration DURATION] [--no-headless]
                               [--notify-config NOTIFY_CONFIG] [--create-notify-config]

Check NVIDIA RTX 5090 stock availability

optional arguments:
  -h, --help            show this help message and exit
  --url URL             URL to check (default: RTX 5090 Founders Edition)
  --monitor             Continuously monitor instead of single check
  --interval INTERVAL   Monitoring interval in seconds (default: 300)
  --duration DURATION   Total monitoring duration in seconds (default: infinite)
  --no-headless         Show browser window (default: headless)
  --notify-config NOTIFY_CONFIG
                        Path to notification configuration file
  --create-notify-config
                        Create sample notification configuration file and exit
```

## Logging

The script creates a `stock_checker.log` file with detailed information about each check:

```bash
# View log in real-time
tail -f stock_checker.log

# Search for in-stock events
grep "IN STOCK" stock_checker.log
```

## Troubleshooting

### ChromeDriver version mismatch
```
Error: This version of ChromeDriver only supports Chrome version X
```

**Solution:** Install matching ChromeDriver version:
```bash
# Check Chrome version
google-chrome --version

# Download matching ChromeDriver from:
# https://chromedriver.chromium.org/downloads
```

### Selenium WebDriver not found
```
selenium.common.exceptions.WebDriverException: 'chromedriver' executable needs to be in PATH
```

**Solution:** Add ChromeDriver to PATH or specify location:
```python
# In nvidia_stock_checker.py, modify setup_driver():
self.driver = webdriver.Chrome(
    executable_path='/path/to/chromedriver',
    options=chrome_options
)
```

### Website structure changed
If the script can't detect stock status, it saves screenshots to help debug:
- Check `screenshot_*.png` files
- Update detection selectors in `_detect_stock_status()` method

### Desktop notifications not working
```bash
# Linux - install notification daemon
sudo apt-get install libnotify-bin

# Install plyer
pip install plyer
```

### Email notifications failing
- Verify SMTP settings are correct
- For Gmail, use an App Password, not your regular password
- Check firewall/antivirus isn't blocking SMTP port 587

## How It Works

1. **Browser Automation**: Uses Selenium WebDriver to load the NVIDIA Marketplace page
2. **Stock Detection**: Checks for multiple indicators:
   - "Add to Cart" or "Buy Now" buttons
   - "Out of Stock" text
   - "In Stock" text
   - Page source analysis
3. **Notification**: When stock is detected, sends alerts via configured methods
4. **Continuous Monitoring**: Repeats checks at specified intervals
5. **Logging**: Records all activity to log file and console

## Best Practices

- **Check Interval**: Don't set intervals too short (recommended minimum: 60 seconds) to avoid being rate-limited
- **Unattended Operation**: Use systemd service or screen for reliable long-term monitoring
- **Multiple Notifications**: Enable multiple notification methods for redundancy
- **Test First**: Run a single check with `--no-headless` to verify it's working correctly
- **Monitor Logs**: Regularly check logs to ensure the script is running properly

## Security Notes

- **Notification Config**: The `notification_config.json` contains sensitive credentials (passwords, tokens)
- **Keep Secure**: Don't commit this file to version control
- **Permissions**: Set appropriate file permissions:
  ```bash
  chmod 600 notification_config.json
  ```

## License

This is a personal automation tool. Use responsibly and in accordance with NVIDIA's terms of service.

## Disclaimer

This tool is for personal use only. The author is not responsible for:
- Any violations of NVIDIA's terms of service
- Failed purchases or missed opportunities
- Any damages resulting from use of this software

Always verify stock availability manually before making a purchase.
