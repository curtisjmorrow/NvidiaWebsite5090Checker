#!/usr/bin/env python3
"""
NVIDIA RTX 5090 Stock Checker
Checks the availability of the NVIDIA GeForce RTX 5090 Founders Edition
on the NVIDIA Marketplace website.
"""

import time
import logging
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import argparse
import sys
import os

try:
    from notifier import Notifier, load_config_from_file, create_sample_config
except ImportError:
    Notifier = None
    logger.warning("Notifier module not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_checker.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class NvidiaStockChecker:
    """Checker for NVIDIA RTX 5090 stock availability"""

    def __init__(self, url, headless=True, notifier=None):
        """
        Initialize the stock checker

        Args:
            url: The NVIDIA marketplace URL to check
            headless: Whether to run browser in headless mode
            notifier: Notifier instance for alerts
        """
        self.url = url
        self.headless = headless
        self.driver = None
        self.notifier = notifier

    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')

        # Randomize user agent to appear more human-like
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        chrome_options.add_argument(f'user-agent={random.choice(user_agents)}')

        # Additional anti-detection measures
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')

        try:
            self.driver = webdriver.Chrome(options=chrome_options)

            # Remove webdriver property to avoid detection
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })

            logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            raise

    def check_stock(self):
        """
        Check if the graphics card is in stock

        Returns:
            dict: Stock status information including availability and timestamp
        """
        if not self.driver:
            self.setup_driver()

        try:
            logger.info(f"Loading URL: {self.url}")
            self.driver.get(self.url)

            # Random wait time to appear more human-like (2-5 seconds)
            wait_time = random.uniform(2.0, 5.0)
            logger.debug(f"Waiting {wait_time:.2f} seconds for page load")
            time.sleep(wait_time)

            # Occasionally scroll to simulate human behavior
            if random.random() < 0.3:  # 30% chance
                try:
                    scroll_amount = random.randint(100, 500)
                    self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                    time.sleep(random.uniform(0.5, 1.5))
                    self.driver.execute_script("window.scrollTo(0, 0);")  # Scroll back to top
                except Exception:
                    pass  # Ignore scroll errors

            # Look for various stock indicators
            stock_status = self._detect_stock_status()

            result = {
                'timestamp': datetime.now().isoformat(),
                'url': self.url,
                'in_stock': stock_status['in_stock'],
                'status_text': stock_status['text'],
                'detection_method': stock_status['method']
            }

            return result

        except Exception as e:
            logger.error(f"Error checking stock: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'url': self.url,
                'in_stock': None,
                'status_text': f'Error: {str(e)}',
                'detection_method': 'error'
            }

    def _detect_stock_status(self):
        """
        Detect stock status using multiple methods

        Returns:
            dict: Detection results with in_stock boolean, text, and method used
        """
        # Method 1: Look for "Add to Cart" or "Buy Now" button
        try:
            add_to_cart_selectors = [
                "//button[contains(text(), 'Add to Cart')]",
                "//button[contains(text(), 'Buy Now')]",
                "//a[contains(text(), 'Add to Cart')]",
                "//a[contains(text(), 'Buy Now')]",
                "//*[@id='add-to-cart']",
                "//button[contains(@class, 'add-to-cart')]"
            ]

            for selector in add_to_cart_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed() and element.is_enabled():
                        logger.info(f"Found active purchase button: {element.text}")
                        return {
                            'in_stock': True,
                            'text': element.text,
                            'method': 'purchase_button'
                        }
                except NoSuchElementException:
                    continue
        except Exception as e:
            logger.debug(f"Error in purchase button detection: {e}")

        # Method 2: Look for "Out of Stock" or similar text
        try:
            out_of_stock_selectors = [
                "//*[contains(text(), 'Out of Stock')]",
                "//*[contains(text(), 'OUT OF STOCK')]",
                "//*[contains(text(), 'Sold Out')]",
                "//*[contains(text(), 'Not Available')]",
                "//*[contains(text(), 'Currently Unavailable')]",
                "//button[@disabled and contains(text(), 'Notify Me')]"
            ]

            for selector in out_of_stock_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        logger.info(f"Found out of stock indicator: {element.text}")
                        return {
                            'in_stock': False,
                            'text': element.text,
                            'method': 'out_of_stock_text'
                        }
                except NoSuchElementException:
                    continue
        except Exception as e:
            logger.debug(f"Error in out of stock detection: {e}")

        # Method 3: Look for "In Stock" text
        try:
            in_stock_selectors = [
                "//*[contains(text(), 'In Stock')]",
                "//*[contains(text(), 'Available')]",
                "//*[contains(@class, 'in-stock')]"
            ]

            for selector in in_stock_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        logger.info(f"Found in stock indicator: {element.text}")
                        return {
                            'in_stock': True,
                            'text': element.text,
                            'method': 'in_stock_text'
                        }
                except NoSuchElementException:
                    continue
        except Exception as e:
            logger.debug(f"Error in stock detection: {e}")

        # Method 4: Save page source for manual inspection
        page_text = self.driver.page_source.lower()
        logger.debug("Checking page source for stock keywords")

        # Check for common stock indicators in page source
        if 'out of stock' in page_text or 'sold out' in page_text:
            return {
                'in_stock': False,
                'text': 'Out of stock (detected in page source)',
                'method': 'page_source'
            }

        if 'add to cart' in page_text or 'buy now' in page_text:
            return {
                'in_stock': True,
                'text': 'Possibly in stock (detected in page source)',
                'method': 'page_source'
            }

        # Save screenshot for debugging
        try:
            screenshot_path = f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved to {screenshot_path}")
        except Exception as e:
            logger.debug(f"Could not save screenshot: {e}")

        # Unable to determine
        return {
            'in_stock': None,
            'text': 'Unable to determine stock status',
            'method': 'unknown'
        }

    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")

    def monitor(self, interval=10, duration=None):
        """
        Continuously monitor stock status

        Args:
            interval: Base time between checks in seconds (default: 10)
            duration: Total duration to monitor in seconds (None = infinite)
        """
        start_time = time.time()
        check_count = 0

        logger.info(f"Starting stock monitoring (base interval: {interval}s with randomization)")

        try:
            while True:
                check_count += 1
                logger.info(f"Check #{check_count}")

                result = self.check_stock()

                if result['in_stock'] is True:
                    logger.warning("PRODUCT IS IN STOCK!")
                    alert_message = f"""
🚨 RTX 5090 IS IN STOCK! 🚨

Status: {result['status_text']}
Time: {result['timestamp']}

👉 BUY NOW:
{result['url']}

Click the link above to purchase immediately!
"""
                    print("\n" + "="*60)
                    print("ALERT: RTX 5090 IS IN STOCK!")
                    print(f"Status: {result['status_text']}")
                    print(f"URL: {result['url']}")
                    print(f"Time: {result['timestamp']}")
                    print("="*60 + "\n")

                    # Send notifications
                    if self.notifier:
                        self.notifier.notify(
                            message=alert_message,
                            title="RTX 5090 IN STOCK!"
                        )

                elif result['in_stock'] is False:
                    logger.info(f"Out of stock - {result['status_text']}")
                else:
                    logger.warning(f"Unclear status - {result['status_text']}")

                # Check if we should stop
                if duration and (time.time() - start_time) >= duration:
                    logger.info(f"Monitoring duration complete ({duration}s)")
                    break

                # Randomize wait time to avoid detection (±20% variation)
                # For 10 second interval: random between 8-12 seconds
                min_wait = interval * 0.8
                max_wait = interval * 1.2
                actual_wait = random.uniform(min_wait, max_wait)

                logger.info(f"Waiting {actual_wait:.1f} seconds until next check...")
                time.sleep(actual_wait)

        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        finally:
            self.close()


def main():
    parser = argparse.ArgumentParser(
        description='Check NVIDIA RTX 5090 stock availability'
    )
    parser.add_argument(
        '--url',
        default='https://marketplace.nvidia.com/en-us/consumer/graphics-cards/geforce-rtx-5090-founders-edition/',
        help='URL to check (default: RTX 5090 Founders Edition)'
    )
    parser.add_argument(
        '--monitor',
        action='store_true',
        help='Continuously monitor instead of single check'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='Monitoring interval in seconds (default: 10, randomized ±20%%)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=None,
        help='Total monitoring duration in seconds (default: infinite)'
    )
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Show browser window (default: headless)'
    )
    parser.add_argument(
        '--notify-config',
        default='notification_config.json',
        help='Path to notification configuration file'
    )
    parser.add_argument(
        '--create-notify-config',
        action='store_true',
        help='Create sample notification configuration file and exit'
    )
    parser.add_argument(
        '--test-notification',
        action='store_true',
        help='Send a test notification and exit'
    )

    args = parser.parse_args()

    # Handle config creation
    if args.create_notify_config:
        if Notifier:
            create_sample_config(args.notify_config)
            print(f"Sample notification config created at {args.notify_config}")
            print("Edit this file to configure your notification preferences.")
        else:
            print("Error: Notifier module not available")
        sys.exit(0)

    # Handle test notification
    if args.test_notification:
        if not Notifier:
            print("Error: Notifier module not available")
            sys.exit(1)

        if not os.path.exists(args.notify_config):
            print(f"Error: Notification config not found at {args.notify_config}")
            print("Run with --create-notify-config first")
            sys.exit(1)

        config = load_config_from_file(args.notify_config)
        notifier = Notifier(config)

        test_message = """
This is a TEST notification from your NVIDIA Stock Checker!

If you're seeing this on your phone, your notifications are working correctly!

Time: {timestamp}
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        print("Sending test notification...")
        success = notifier.notify(
            message=test_message,
            title="Test Notification - Stock Checker"
        )

        if success:
            print("✓ Test notification sent successfully!")
            print("Check your phone/desktop for the notification.")
        else:
            print("✗ Failed to send test notification.")
            print("Check the logs above for error details.")

        sys.exit(0)

    # Load notification config
    notifier = None
    if Notifier and os.path.exists(args.notify_config):
        config = load_config_from_file(args.notify_config)
        notifier = Notifier(config)
        logger.info(f"Loaded notification config from {args.notify_config}")
    elif Notifier:
        logger.info("No notification config found, notifications disabled")

    checker = NvidiaStockChecker(
        url=args.url,
        headless=not args.no_headless,
        notifier=notifier
    )

    try:
        if args.monitor:
            checker.monitor(interval=args.interval, duration=args.duration)
        else:
            result = checker.check_stock()

            print("\n" + "="*60)
            print("NVIDIA RTX 5090 Stock Check Result")
            print("="*60)
            print(f"Time: {result['timestamp']}")
            print(f"URL: {result['url']}")
            print(f"In Stock: {result['in_stock']}")
            print(f"Status: {result['status_text']}")
            print(f"Detection Method: {result['detection_method']}")
            print("="*60 + "\n")

            checker.close()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
