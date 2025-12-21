#!/bin/bash
# Quick setup script for NVIDIA Stock Checker

echo "NVIDIA RTX 5090 Stock Checker - Setup"
echo "======================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Error: Python 3 is required"; exit 1; }
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt || { echo "Error: Failed to install dependencies"; exit 1; }
echo ""

# Check for ChromeDriver
echo "Checking for ChromeDriver..."
if command -v chromedriver &> /dev/null; then
    echo "ChromeDriver found: $(chromedriver --version)"
else
    echo "WARNING: ChromeDriver not found!"
    echo "Please install ChromeDriver:"
    echo "  - Ubuntu/Debian: sudo apt-get install chromium-chromedriver"
    echo "  - macOS: brew install chromedriver"
    echo "  - Windows: Download from https://chromedriver.chromium.org/downloads"
    echo ""
fi

# Create notification config
echo "Creating sample notification configuration..."
python3 nvidia_stock_checker.py --create-notify-config || true
echo ""

echo "Setup complete!"
echo ""
echo "Quick start:"
echo "  1. Edit notification_config.json to configure notifications"
echo "  2. Run: python3 nvidia_stock_checker.py --monitor"
echo ""
echo "For more information, see README.md"
