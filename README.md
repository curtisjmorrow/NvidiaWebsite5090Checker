# NVIDIA RTX 5090 Stock Checker

Automatically monitor the NVIDIA Marketplace for RTX 5090 Founders Edition stock and get instant notifications on your phone when it's available!

## Features

- 📱 **Instant phone notifications** via Telegram
- 🤖 **Automated monitoring** - runs in background 24/7
- 🔍 **Multiple detection methods** for reliable stock checking
- 📊 **Detailed logging** of all checks and status changes
- ⚙️ **Configurable check intervals** (default: every 10 seconds with randomization)
- 🌐 **Multiple notification options** (Telegram, email, desktop, Discord, webhooks)
- 🖥️ **Headless mode** for efficient background operation

## Quick Start for Windows 11

This guide will get you up and running in about 10 minutes with Telegram notifications on your phone.

### Prerequisites Check

**Do you have Python installed?**
```powershell
python --version
```
If you see a version number (3.7+), skip to Step 2. Otherwise, continue:

**Install Python:**
1. Download from https://www.python.org/downloads/
2. Run installer
3. ✅ **IMPORTANT**: Check "Add Python to PATH" during installation
4. Click "Install Now"
5. Restart PowerShell after installation

**Do you have Git installed?**
```powershell
git --version
```
If you see a version number, skip to Step 1. Otherwise:
- Download from https://git-scm.com/download/win
- Install with default settings

### Step 1: Download the Project

Open PowerShell (`Win + X` → "Windows PowerShell" or "Terminal"):

```powershell
# Navigate to your Documents folder
cd $HOME\Documents

# Download the project
git clone https://github.com/curtisjmorrow/NvidiaWebsite5090Checker.git
cd NvidiaWebsite5090Checker
```

### Step 2: Install ChromeDriver

Choose one method:

**Option A: Using winget (Easiest)**
```powershell
winget install Google.Chrome
winget install Chromium.ChromeDriver
```

**Option B: Manual Installation**
1. Open Chrome and go to `chrome://version`
2. Note your Chrome version (e.g., "120.0.6099.109")
3. Download matching ChromeDriver from https://chromedriver.chromium.org/downloads
4. Extract `chromedriver.exe` to `C:\Program Files\ChromeDriver\`
5. Add to PATH:
   ```powershell
   # Run PowerShell as Administrator
   $env:Path += ";C:\Program Files\ChromeDriver\"
   [Environment]::SetEnvironmentVariable("Path", $env:Path, [EnvironmentVariableTarget]::Machine)
   ```
6. Restart PowerShell

**Verify ChromeDriver:**
```powershell
chromedriver --version
# Should show: ChromeDriver 120.0.6099.109 (or similar)
```

### Step 3: Install Python Dependencies

```powershell
# Install Selenium (required)
pip install -r requirements.txt

# Install requests for Telegram notifications (required for phone alerts)
pip install requests
```

### Step 4: Set Up Telegram Notifications

This is the best way to get notified on your phone!

#### 4.1 Install Telegram

- **iPhone**: https://apps.apple.com/app/telegram-messenger/id686449807
- **Android**: https://play.google.com/store/apps/details?id=org.telegram.messenger

#### 4.2 Create Your Bot

1. Open Telegram and search for `@BotFather`
2. Send: `/start`
3. Send: `/newbot`
4. Choose a name: `Stock Alert` (or anything you like)
5. Choose a username: `mystockalert_bot` (must be unique and end with `_bot`)
6. **Copy the bot token** - looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

#### 4.3 Get Your Chat ID

1. Search for your bot in Telegram (use the username you created)
2. Send it any message (just say "hi")
3. Open this URL in your browser (replace `YOUR_BOT_TOKEN` with your actual token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. Look for `"chat":{"id":987654321` in the response
5. **Copy that number** - this is your Chat ID

#### 4.4 Configure Notifications

```powershell
# Create notification config file
python nvidia_stock_checker.py --create-notify-config

# Edit the config file
notepad notification_config.json
```

**Replace the telegram section** with your information:
```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
    "chat_id": "987654321"
  },
  "desktop": {
    "enabled": false
  },
  "email": {
    "enabled": false
  }
}
```

Replace:
- `123456789:ABCdefGHIjklMNOpqrsTUVwxyz` with YOUR bot token
- `987654321` with YOUR chat ID

Save and close Notepad.

### Step 5: Test the Script

```powershell
# Run a quick test (visible browser window)
python nvidia_stock_checker.py --no-headless
```

You should see:
- Chrome browser opens
- Script loads the NVIDIA page
- Logs show "Out of stock" or current status
- Browser closes

Check the log file to verify Telegram is configured:
```powershell
notepad stock_checker.log
```

### Step 6: Start Monitoring

**Run in background (hidden):**
```powershell
Start-Process python -ArgumentList "nvidia_stock_checker.py --monitor" -WindowStyle Hidden
```

**That's it!** The script is now running in the background, checking every 10 seconds (randomized 8-12 seconds to avoid detection). When the RTX 5090 comes in stock, you'll get an instant Telegram message on your phone!

## Managing the Background Process

### View the Log

```powershell
# Open log file
notepad stock_checker.log

# View in real-time
Get-Content stock_checker.log -Wait
```

### Stop the Script

1. Open Task Manager (`Ctrl + Shift + Esc`)
2. Find "Python" processes
3. Right-click → End Task

### Check if It's Running

```powershell
# List all Python processes
Get-Process python
```

## Running on Startup (Optional)

To have the script start automatically when Windows starts:

### Method 1: Task Scheduler (Recommended)

1. Press `Win + R`, type `taskschd.msc`, press Enter
2. Click "Create Basic Task"
3. Name: "NVIDIA Stock Checker"
4. Trigger: "When I log on"
5. Action: "Start a program"
   - Program: `python.exe`
   - Arguments: `nvidia_stock_checker.py --monitor`
   - Start in: `C:\Users\YourName\Documents\NvidiaWebsite5090Checker`
6. Finish and test by right-clicking the task → Run

### Method 2: Startup Folder

Create a `.bat` file:
```batch
@echo off
cd C:\Users\YourName\Documents\NvidiaWebsite5090Checker
pythonw nvidia_stock_checker.py --monitor
```

Save as `start_stock_checker.bat` and place in:
```
C:\Users\YourName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

## Customization

### Change Check Interval

```powershell
# Check every 2 minutes (120 seconds)
python nvidia_stock_checker.py --monitor --interval 120

# Check every 30 seconds (faster, but more resource intensive)
python nvidia_stock_checker.py --monitor --interval 30
```

**Recommended**: Keep interval at 60 seconds or higher to avoid rate limiting.

### Check Different Product

```powershell
python nvidia_stock_checker.py --url "https://marketplace.nvidia.com/en-us/..." --monitor
```

### Enable Multiple Notifications

Edit `notification_config.json` to enable multiple methods:

```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID"
  },
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-gmail-app-password",
    "recipient_email": "your-email@gmail.com"
  },
  "desktop": {
    "enabled": true
  }
}
```

**For Gmail**: Create an App Password at https://myaccount.google.com/apppasswords

**For desktop notifications**: Install `pip install plyer`

## Troubleshooting

### "python is not recognized"
- Python isn't installed or not in PATH
- Reinstall Python and check "Add Python to PATH"
- Restart PowerShell

### "chromedriver is not recognized"
- ChromeDriver isn't in PATH
- Run: `chromedriver --version` to test
- Reinstall using winget or add to PATH manually
- Restart PowerShell

### "No module named 'selenium'"
```powershell
pip install selenium
```

### "Failed to send Telegram notification"
- Verify bot token is correct (should include `:`)
- Verify chat ID is correct (just numbers)
- Make sure you sent your bot a message first
- Check: `pip install requests`

### Script says "Unable to determine stock status"
- Check `screenshot_*.png` files to see what the page looks like
- The website structure may have changed
- Check `stock_checker.log` for details

### Chrome/ChromeDriver version mismatch
```
This version of ChromeDriver only supports Chrome version X
```
- Update Chrome: `winget upgrade Google.Chrome`
- Update ChromeDriver: `winget upgrade Chromium.ChromeDriver`
- Or download matching version from https://chromedriver.chromium.org/downloads

### Script stops running
- Check Task Manager to see if it crashed
- Check `stock_checker.log` for errors
- Use Task Scheduler to auto-restart on failure

## Linux / macOS Setup

<details>
<summary>Click to expand Linux/macOS instructions</summary>

### Linux (Ubuntu/Debian)

```bash
# Clone repository
git clone https://github.com/curtisjmorrow/NvidiaWebsite5090Checker.git
cd NvidiaWebsite5090Checker

# Install ChromeDriver
sudo apt-get update
sudo apt-get install chromium-chromedriver

# Install dependencies
pip3 install -r requirements.txt
pip3 install requests

# Set up Telegram (same as Windows steps 4.2-4.4)
python3 nvidia_stock_checker.py --create-notify-config
nano notification_config.json

# Run
python3 nvidia_stock_checker.py --monitor

# Run in background with screen
screen -S nvidia-checker
python3 nvidia_stock_checker.py --monitor
# Press Ctrl+A then D to detach
# Reattach: screen -r nvidia-checker
```

### macOS

```bash
# Clone repository
git clone https://github.com/curtisjmorrow/NvidiaWebsite5090Checker.git
cd NvidiaWebsite5090Checker

# Install ChromeDriver
brew install chromedriver

# Install dependencies
pip3 install -r requirements.txt
pip3 install requests

# Set up Telegram (same as Windows steps 4.2-4.4)
python3 nvidia_stock_checker.py --create-notify-config
nano notification_config.json

# Run
python3 nvidia_stock_checker.py --monitor
```

</details>

## Command-Line Options

```
usage: nvidia_stock_checker.py [-h] [--url URL] [--monitor]
                               [--interval INTERVAL] [--duration DURATION]
                               [--no-headless] [--notify-config NOTIFY_CONFIG]
                               [--create-notify-config]

Options:
  -h, --help            Show help message
  --url URL             URL to check (default: RTX 5090 Founders Edition)
  --monitor             Continuously monitor instead of single check
  --interval INTERVAL   Check interval in seconds (default: 300)
  --duration DURATION   Total monitoring duration in seconds (default: infinite)
  --no-headless         Show browser window (useful for debugging)
  --notify-config FILE  Path to notification config file
  --create-notify-config Create sample notification config and exit
```

## Examples

```powershell
# Single check
python nvidia_stock_checker.py

# Monitor with default settings (every 10 seconds, randomized)
python nvidia_stock_checker.py --monitor

# Monitor every 2 minutes
python nvidia_stock_checker.py --monitor --interval 120

# Monitor for 1 hour only
python nvidia_stock_checker.py --monitor --duration 3600

# Monitor with visible browser (debugging)
python nvidia_stock_checker.py --monitor --no-headless

# Run in background (Windows)
Start-Process python -ArgumentList "nvidia_stock_checker.py --monitor" -WindowStyle Hidden

# Run in background (Linux/macOS)
nohup python3 nvidia_stock_checker.py --monitor > output.log 2>&1 &
```

## How It Works

1. **Browser Automation**: Uses Selenium WebDriver to load the NVIDIA Marketplace page like a real browser
2. **Stock Detection**: Checks for multiple indicators:
   - "Add to Cart" or "Buy Now" buttons (in stock)
   - "Out of Stock" or "Sold Out" text (out of stock)
   - "In Stock" text (in stock)
   - Page source analysis as fallback
3. **Notification**: When stock is detected, sends alerts via configured methods
4. **Continuous Monitoring**: Repeats checks at specified intervals
5. **Logging**: Records all checks, status changes, and errors to `stock_checker.log`
6. **Screenshots**: Captures page screenshots when status is unclear for debugging

## What You'll Receive

When the RTX 5090 is in stock, you'll get a Telegram message like:

```
RTX 5090 IN STOCK!

Status: Add to Cart
URL: https://marketplace.nvidia.com/en-us/consumer/graphics-cards/geforce-rtx-5090-founders-edition/
Time: 2025-12-26T10:30:45

Go buy it now!
```

### Notification Speed

With the default 10-second interval:
- **Average notification time**: ~15-20 seconds after stock appears
- **Worst case**: ~22 seconds
- **Best case**: ~7-12 seconds

The script checks every 8-12 seconds (randomized to avoid bot detection), so you'll be notified within about 15-20 seconds on average - **much faster than manual checking!**

## Important Notes

### Rate Limiting
- Default 10 seconds (randomized 8-12s) balances speed with safety
- Randomization helps avoid detection patterns
- NVIDIA may rate-limit or block if you go much faster
- Script includes anti-bot measures (random user agents, scrolling, timing)

### Resource Usage
- Headless mode uses ~200-300 MB RAM per Chrome instance
- Each check takes 5-10 seconds
- Log file grows over time (safe to delete periodically)

### Privacy & Security
- `notification_config.json` contains sensitive credentials
- Never commit or share this file
- It's already in `.gitignore` to prevent accidental commits
- Your bot token is like a password - keep it private

### Legal & Terms of Service
- This tool is for personal use only
- Ensure compliance with NVIDIA's terms of service
- The author is not responsible for any violations or issues
- Always verify stock manually before purchasing

## Files Generated

- `stock_checker.log` - Detailed log of all checks and events
- `notification_config.json` - Your notification settings (keep private!)
- `screenshot_*.png` - Debug screenshots when status is unclear
- `__pycache__/` - Python bytecode cache (safe to ignore)

## Updating the Script

To get the latest version:

```powershell
cd NvidiaWebsite5090Checker
git pull
```

## Support & Contributing

- **Issues**: Report bugs at https://github.com/curtisjmorrow/NvidiaWebsite5090Checker/issues
- **Questions**: Check the log file first, then open an issue
- **Contributing**: Pull requests welcome!

## Other Notification Methods

<details>
<summary>Email Notifications (Gmail)</summary>

1. Create App Password: https://myaccount.google.com/apppasswords
2. Edit `notification_config.json`:
```json
{
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",
    "sender_password": "16-char-app-password",
    "recipient_email": "your-email@gmail.com"
  }
}
```

</details>

<details>
<summary>Discord Webhook</summary>

1. Go to Discord Server Settings → Integrations → Webhooks
2. Create webhook and copy URL
3. Edit `notification_config.json`:
```json
{
  "discord": {
    "enabled": true,
    "webhook_url": "https://discord.com/api/webhooks/..."
  }
}
```
4. Install: `pip install requests`

</details>

<details>
<summary>Desktop Notifications (Windows/macOS/Linux)</summary>

```powershell
# Install plyer
pip install plyer

# Edit notification_config.json
{
  "desktop": {
    "enabled": true
  }
}
```

Note: Only works when you're logged in and at your computer

</details>

## License

This is a personal automation tool. Use responsibly and in accordance with NVIDIA's terms of service.

## Disclaimer

This tool is for personal use only. The author is not responsible for:
- Any violations of NVIDIA's terms of service
- Failed purchases or missed opportunities
- Any damages resulting from use of this software
- Rate limiting or blocking by NVIDIA

Always verify stock availability manually before making a purchase.

---

**Good luck getting your RTX 5090!** 🎮🚀
