# Telegram Notifications Setup Guide

Get instant notifications on your phone when the RTX 5090 comes in stock!

## Why Telegram?

- ✅ **Completely free** - No SMS or email fees
- ✅ **Instant push notifications** - Get alerted immediately
- ✅ **Works anywhere** - Phone, tablet, desktop
- ✅ **Easy setup** - Takes 2-3 minutes
- ✅ **Reliable** - No spam filters like email

## Setup Steps

### Step 1: Install Telegram (if you don't have it)

- **iPhone**: Download from [App Store](https://apps.apple.com/app/telegram-messenger/id686449807)
- **Android**: Download from [Google Play](https://play.google.com/store/apps/details?id=org.telegram.messenger)
- **Desktop**: Download from [telegram.org](https://desktop.telegram.org/)

### Step 2: Create Your Bot

1. **Open Telegram** on your phone or computer

2. **Search for BotFather**:
   - In the search bar, type `@BotFather`
   - Click on the verified bot (it has a checkmark)

3. **Create your bot**:
   - Send: `/start`
   - Send: `/newbot`
   - BotFather will ask for a name: `Stock Alert` (or any name you like)
   - BotFather will ask for a username: `mystockalert123_bot` (must end with `_bot` and be unique)

4. **Copy your Bot Token**:
   - BotFather will send you a message like:
     ```
     Done! Congratulations on your new bot...
     Use this token to access the HTTP API:
     123456789:ABCdefGHIjklMNOpqrsTUVwxyz
     ```
   - **SAVE THIS TOKEN** - You'll need it in Step 4

### Step 3: Get Your Chat ID

1. **Start a chat with your bot**:
   - Click the link BotFather sent you, or search for your bot's username
   - Send your bot any message (like "hi" or "test")

2. **Get your Chat ID**:
   - Open this URL in your browser (replace `YOUR_BOT_TOKEN` with the token from Step 2):
     ```
     https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
     ```
   - You'll see something like:
     ```json
     {"ok":true,"result":[{"update_id":123,"message":{"message_id":1,"from":{"id":987654321,...},"chat":{"id":987654321,...}}}]}
     ```
   - Find the `"chat":{"id":987654321` number
   - **SAVE THIS NUMBER** - This is your Chat ID

**Quick Tip**: If you don't see any results, make sure you sent a message to your bot first!

### Step 4: Configure the Stock Checker

On your Windows PC:

```powershell
# 1. Install the requests package (needed for Telegram)
pip install requests

# 2. Create the notification config file
python nvidia_stock_checker.py --create-notify-config

# 3. Open the config file
notepad notification_config.json
```

### Step 5: Edit notification_config.json

Replace the Telegram section with your bot token and chat ID:

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

**Important**:
- Replace `123456789:ABCdefGHIjklMNOpqrsTUVwxyz` with YOUR bot token
- Replace `987654321` with YOUR chat ID
- Keep the quotes around both values

Save and close the file.

### Step 6: Test It!

```powershell
# Run a test to make sure Telegram notifications work
python nvidia_stock_checker.py --monitor --no-headless --interval 60
```

Watch for about 1 minute. You should see the script checking the website. While you won't get a "stock found" alert (unless it's actually in stock), you can verify:
- The script is running without errors
- Check the log file for any Telegram errors: `notepad stock_checker.log`

If you see `"Telegram notification sent to chat 987654321"` in the logs, you're all set!

### Step 7: Run in Background

Once confirmed working:

```powershell
# Run hidden in background
Start-Process python -ArgumentList "nvidia_stock_checker.py --monitor" -WindowStyle Hidden
```

Now go about your day! You'll get a Telegram message on your phone when stock is found.

## Troubleshooting

### "Failed to send Telegram notification"

**Check #1**: Make sure you installed requests:
```powershell
pip install requests
```

**Check #2**: Verify your bot token is correct:
- Should look like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
- Must include the colon `:`
- No spaces before or after

**Check #3**: Verify your chat ID is correct:
- Should be just numbers (like `987654321`)
- No quotes in the actual number
- Could be negative (like `-987654321`) for groups

**Check #4**: Make sure you started a chat with your bot:
- Search for your bot in Telegram
- Send it a message
- Try getting the chat ID again

### "Connection timeout" or "Network error"

- Check your internet connection
- Try again - Telegram servers might be temporarily busy
- Make sure your firewall isn't blocking Python

### Not receiving notifications on phone

- Check Telegram notification settings on your phone
- Make sure Telegram app is not in battery optimization mode
- Try sending a test message to your bot manually

## Advanced: Multiple Notification Methods

Want both Telegram AND email? Enable both:

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
  }
}
```

Now you'll get notified via both Telegram AND email for maximum reliability!

## What the Notification Looks Like

When stock is found, you'll receive a Telegram message like:

```
RTX 5090 IN STOCK!

Status: Add to Cart
URL: https://marketplace.nvidia.com/en-us/consumer/graphics-cards/geforce-rtx-5090-founders-edition/
Time: 2025-12-26T10:30:45.123456

Go buy it now!
```

## Privacy & Security

- Your bot token is like a password - keep it private
- Don't share your notification_config.json file (it's in .gitignore)
- Only you can message your bot (unless you add others)
- Telegram messages are encrypted

## Quick Reference

**Get Bot Token**:
1. Message @BotFather in Telegram
2. Send `/newbot`
3. Follow the prompts
4. Copy the token

**Get Chat ID**:
1. Send your bot a message
2. Visit: `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
3. Find `"chat":{"id":NUMBER}`
4. Copy that number

**Config File Location**: `notification_config.json` in the same folder as the script

**Test Command**: `python nvidia_stock_checker.py --monitor --no-headless --interval 60`

**Run Command**: `Start-Process python -ArgumentList "nvidia_stock_checker.py --monitor" -WindowStyle Hidden`

---

Need help? Check the main README.md or WINDOWS_SETUP.md for more information!
