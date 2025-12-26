# Quick Start Guide: Running from GitHub on Windows 11

This guide will help you download and run the NVIDIA RTX 5090 Stock Checker directly from GitHub on your Windows 11 PC.

## Prerequisites

### 1. Install Git for Windows (if not already installed)

**Check if Git is installed:**
```powershell
git --version
```

If you see a version number, skip to step 2. If not, install Git:

- Download from: https://git-scm.com/download/win
- Run the installer with default settings
- Restart PowerShell after installation

### 2. Install Python (if not already installed)

**Check if Python is installed:**
```powershell
python --version
```

If you see a version number (3.7+), you're good. If not:

1. Download from: https://www.python.org/downloads/
2. Run the installer
3. **IMPORTANT**: Check the box "Add Python to PATH" during installation
4. Click "Install Now"
5. Restart PowerShell after installation

## Installation Steps

### Step 1: Open PowerShell

1. Press `Win + X`
2. Select "Windows PowerShell" or "Terminal"

### Step 2: Choose a Directory

Navigate to where you want to download the project:
```powershell
# Option 1: Download to your Documents folder
cd $HOME\Documents

# Option 2: Download to your Desktop
cd $HOME\Desktop

# Option 3: Create a dedicated folder
mkdir C:\Projects
cd C:\Projects
```

### Step 3: Clone the Repository

```powershell
git clone https://github.com/curtisjmorrow/NvidiaWebsite5090Checker.git
cd NvidiaWebsite5090Checker
```

### Step 4: Install Python Dependencies

```powershell
pip install -r requirements.txt
```

This will install Selenium (the main requirement).

### Step 5: Install ChromeDriver

**Option A: Using winget (Recommended - Easiest)**
```powershell
# Install Chrome (if not already installed)
winget install Google.Chrome

# Install ChromeDriver
winget install Chromium.ChromeDriver
```

**Option B: Manual Installation**

1. Check your Chrome version:
   - Open Chrome
   - Go to `chrome://version`
   - Note the version number (e.g., "120.0.6099.109")

2. Download matching ChromeDriver:
   - Visit: https://chromedriver.chromium.org/downloads
   - Download the version matching your Chrome
   - Extract `chromedriver.exe`

3. Add to PATH:
   - Create folder: `C:\Program Files\ChromeDriver\`
   - Move `chromedriver.exe` into that folder
   - Add to PATH:
     ```powershell
     # Run PowerShell as Administrator
     $env:Path += ";C:\Program Files\ChromeDriver\"
     [Environment]::SetEnvironmentVariable("Path", $env:Path, [EnvironmentVariableTarget]::Machine)
     ```

### Step 6: Verify Installation

```powershell
# Check if ChromeDriver is accessible
chromedriver --version

# Should show something like: ChromeDriver 120.0.6099.109
```

### Step 7: Run the Stock Checker

**Single Check (test run):**
```powershell
python nvidia_stock_checker.py
```

**Continuous Monitoring (checks every 5 minutes):**
```powershell
python nvidia_stock_checker.py --monitor
```

**Monitor with custom interval (e.g., every 2 minutes):**
```powershell
python nvidia_stock_checker.py --monitor --interval 120
```

**Run with visible browser (to see what's happening):**
```powershell
python nvidia_stock_checker.py --monitor --no-headless
```

## Optional: Set Up Notifications

### Create Notification Config
```powershell
python nvidia_stock_checker.py --create-notify-config
```

This creates `notification_config.json`. Edit it with Notepad:
```powershell
notepad notification_config.json
```

Enable desktop notifications (easiest option for Windows):
```json
{
  "desktop": {
    "enabled": true
  }
}
```

For desktop notifications to work, install the plyer package:
```powershell
pip install plyer
```

## Running in Background

Once you've confirmed it works, run it in the background:

**Option 1: Hidden Window (Simplest)**
```powershell
Start-Process python -ArgumentList "nvidia_stock_checker.py --monitor" -WindowStyle Hidden
```

**Option 2: No Console Window**
```powershell
pythonw nvidia_stock_checker.py --monitor
```

**Option 3: Background Job**
```powershell
Start-Job -ScriptBlock {
    Set-Location "C:\path\to\NvidiaWebsite5090Checker"
    python nvidia_stock_checker.py --monitor
}

# Check status
Get-Job

# View output
Receive-Job -Id 1 -Keep
```

## Viewing Logs

The script creates a log file you can check:

```powershell
# View log in real-time
Get-Content stock_checker.log -Wait

# Or open in Notepad
notepad stock_checker.log
```

## Stopping the Script

If running in a visible window:
- Press `Ctrl + C`

If running in background:
- Open Task Manager (`Ctrl + Shift + Esc`)
- Find "Python" processes
- Right-click → End Task

If running as a job:
```powershell
# List jobs
Get-Job

# Stop job
Stop-Job -Id 1
Remove-Job -Id 1
```

## Troubleshooting

### "python is not recognized"
- Python isn't installed or not in PATH
- Reinstall Python and check "Add Python to PATH"
- Restart PowerShell

### "chromedriver is not recognized"
- ChromeDriver isn't installed or not in PATH
- Follow Step 5 again carefully
- Restart PowerShell

### "No module named 'selenium'"
```powershell
pip install selenium
```

### Script can't find Chrome
Make sure Chrome is installed:
```powershell
winget install Google.Chrome
```

### Permission Denied Errors
Run PowerShell as Administrator:
- Right-click PowerShell
- Select "Run as Administrator"

## Updating the Script

To get the latest version:
```powershell
cd NvidiaWebsite5090Checker
git pull
```

## Complete Example (All Commands)

Here's the complete sequence for a fresh Windows 11 install:

```powershell
# 1. Navigate to where you want the project
cd $HOME\Documents

# 2. Clone the repository
git clone https://github.com/curtisjmorrow/NvidiaWebsite5090Checker.git
cd NvidiaWebsite5090Checker

# 3. Install ChromeDriver
winget install Google.Chrome
winget install Chromium.ChromeDriver

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. (Optional) Set up desktop notifications
pip install plyer
python nvidia_stock_checker.py --create-notify-config
notepad notification_config.json
# Edit: set "desktop": {"enabled": true}

# 6. Test it works (visible browser)
python nvidia_stock_checker.py --no-headless

# 7. Run in background
Start-Process python -ArgumentList "nvidia_stock_checker.py --monitor" -WindowStyle Hidden

# 8. Check logs
Get-Content stock_checker.log -Wait
```

## Need Help?

- Check the main README.md for more details
- Check stock_checker.log for error messages
- Make sure Chrome and ChromeDriver versions match
