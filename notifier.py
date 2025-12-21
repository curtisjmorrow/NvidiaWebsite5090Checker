#!/usr/bin/env python3
"""
Notification module for stock alerts
Supports multiple notification methods: email, desktop, sound, webhook
"""

import logging
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class Notifier:
    """Handles various notification methods for stock alerts"""

    def __init__(self, config=None):
        """
        Initialize notifier with configuration

        Args:
            config: Dictionary with notification settings
        """
        self.config = config or {}

    def notify(self, message, title="Stock Alert"):
        """
        Send notification using all enabled methods

        Args:
            message: The notification message
            title: The notification title
        """
        success = False

        # Try email notification
        if self.config.get('email', {}).get('enabled'):
            if self._send_email(message, title):
                success = True

        # Try desktop notification
        if self.config.get('desktop', {}).get('enabled'):
            if self._send_desktop_notification(message, title):
                success = True

        # Try webhook notification
        if self.config.get('webhook', {}).get('enabled'):
            if self._send_webhook(message, title):
                success = True

        # Try sound alert
        if self.config.get('sound', {}).get('enabled'):
            if self._play_sound():
                success = True

        # Try Telegram notification
        if self.config.get('telegram', {}).get('enabled'):
            if self._send_telegram(message, title):
                success = True

        # Try Discord webhook
        if self.config.get('discord', {}).get('enabled'):
            if self._send_discord(message, title):
                success = True

        return success

    def _send_email(self, message, title):
        """Send email notification"""
        try:
            email_config = self.config['email']

            smtp_server = email_config.get('smtp_server')
            smtp_port = email_config.get('smtp_port', 587)
            sender_email = email_config.get('sender_email')
            sender_password = email_config.get('sender_password')
            recipient_email = email_config.get('recipient_email')

            if not all([smtp_server, sender_email, sender_password, recipient_email]):
                logger.warning("Email config incomplete, skipping email notification")
                return False

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"{title} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            body = f"""
{title}

{message}

Timestamp: {datetime.now().isoformat()}

This is an automated notification from your NVIDIA Stock Checker.
"""

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)

            logger.info(f"Email notification sent to {recipient_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False

    def _send_desktop_notification(self, message, title):
        """Send desktop notification (Linux/macOS/Windows)"""
        try:
            # Try using plyer (cross-platform)
            try:
                from plyer import notification
                notification.notify(
                    title=title,
                    message=message,
                    app_name='NVIDIA Stock Checker',
                    timeout=10
                )
                logger.info("Desktop notification sent (plyer)")
                return True
            except ImportError:
                pass

            # Fallback to platform-specific methods
            import platform
            system = platform.system()

            if system == 'Linux':
                os.system(f'notify-send "{title}" "{message}"')
                logger.info("Desktop notification sent (notify-send)")
                return True
            elif system == 'Darwin':  # macOS
                os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
                logger.info("Desktop notification sent (osascript)")
                return True
            elif system == 'Windows':
                # Try using Windows toast notifications
                try:
                    from win10toast import ToastNotifier
                    toaster = ToastNotifier()
                    toaster.show_toast(title, message, duration=10)
                    logger.info("Desktop notification sent (win10toast)")
                    return True
                except ImportError:
                    logger.warning("win10toast not installed, skipping Windows notification")
                    return False

        except Exception as e:
            logger.error(f"Failed to send desktop notification: {e}")
            return False

    def _send_webhook(self, message, title):
        """Send generic webhook notification"""
        try:
            import requests

            webhook_url = self.config['webhook'].get('url')
            if not webhook_url:
                return False

            payload = {
                'title': title,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }

            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info(f"Webhook notification sent to {webhook_url}")
            return True

        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False

    def _send_telegram(self, message, title):
        """Send Telegram notification"""
        try:
            import requests

            telegram_config = self.config['telegram']
            bot_token = telegram_config.get('bot_token')
            chat_id = telegram_config.get('chat_id')

            if not all([bot_token, chat_id]):
                logger.warning("Telegram config incomplete")
                return False

            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': f"*{title}*\n\n{message}",
                'parse_mode': 'Markdown'
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info(f"Telegram notification sent to chat {chat_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False

    def _send_discord(self, message, title):
        """Send Discord webhook notification"""
        try:
            import requests

            discord_webhook_url = self.config['discord'].get('webhook_url')
            if not discord_webhook_url:
                return False

            payload = {
                'embeds': [{
                    'title': title,
                    'description': message,
                    'color': 0x76B900,  # NVIDIA green
                    'timestamp': datetime.now().isoformat(),
                    'footer': {
                        'text': 'NVIDIA Stock Checker'
                    }
                }]
            }

            response = requests.post(discord_webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info("Discord notification sent")
            return True

        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
            return False

    def _play_sound(self):
        """Play sound alert"""
        try:
            # Try using playsound
            try:
                from playsound import playsound
                sound_file = self.config['sound'].get('file')
                if sound_file and os.path.exists(sound_file):
                    playsound(sound_file)
                    logger.info(f"Played sound: {sound_file}")
                    return True
            except ImportError:
                pass

            # Fallback to system beep
            import platform
            if platform.system() == 'Linux':
                os.system('beep')
            elif platform.system() == 'Darwin':
                os.system('afplay /System/Library/Sounds/Glass.aiff')
            elif platform.system() == 'Windows':
                import winsound
                winsound.Beep(1000, 500)

            logger.info("System beep played")
            return True

        except Exception as e:
            logger.error(f"Failed to play sound: {e}")
            return False


def load_config_from_file(config_file='notification_config.json'):
    """
    Load notification configuration from JSON file

    Args:
        config_file: Path to the configuration file

    Returns:
        dict: Configuration dictionary
    """
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config from {config_file}: {e}")

    return {}


def create_sample_config(config_file='notification_config.json'):
    """Create a sample configuration file"""
    sample_config = {
        "email": {
            "enabled": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "your-email@gmail.com",
            "sender_password": "your-app-password",
            "recipient_email": "recipient@example.com"
        },
        "desktop": {
            "enabled": True
        },
        "sound": {
            "enabled": True,
            "file": ""
        },
        "telegram": {
            "enabled": False,
            "bot_token": "your-bot-token",
            "chat_id": "your-chat-id"
        },
        "discord": {
            "enabled": False,
            "webhook_url": "https://discord.com/api/webhooks/..."
        },
        "webhook": {
            "enabled": False,
            "url": "https://your-webhook-url.com/notify"
        }
    }

    with open(config_file, 'w') as f:
        json.dump(sample_config, f, indent=4)

    logger.info(f"Sample config created at {config_file}")
    return sample_config
