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

    def __init__(self, urls, headless=True, notifier=None):
        """
        Initialize the stock checker

        Args:
            urls: List of URLs to check or single URL string
            headless: Whether to run browser in headless mode
            notifier: Notifier instance for alerts
        """
        # Convert single URL to list
        if isinstance(urls, str):
            self.urls = [urls]
        else:
            self.urls = urls
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

        # Fix HTTP2 protocol errors
        chrome_options.add_argument('--disable-http2')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')

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

            # Set page load timeout to 30 seconds
            self.driver.set_page_load_timeout(30)

            # Set script timeout
            self.driver.set_script_timeout(30)

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

    def check_stock(self, url):
        """
        Check if the graphics card is in stock at a specific URL

        Args:
            url: The URL to check

        Returns:
            dict: Stock status information including availability and timestamp
        """
        if not self.driver:
            self.setup_driver()

        try:
            logger.info(f"Loading URL: {url}")

            try:
                self.driver.get(url)
            except TimeoutException:
                logger.error("Page load timeout - restarting driver")
                self.close()
                self.setup_driver()
                return {
                    'timestamp': datetime.now().isoformat(),
                    'url': url,
                    'in_stock': None,
                    'status_text': 'Page load timeout - will retry next check',
                    'detection_method': 'timeout'
                }

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
                'url': url,
                'in_stock': stock_status['in_stock'],
                'status_text': stock_status['text'],
                'detection_method': stock_status['method']
            }

            return result

        except TimeoutException as e:
            logger.error(f"Timeout error checking stock: {e}")
            # Restart driver on timeout
            self.close()
            return {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'in_stock': None,
                'status_text': 'Timeout error - driver restarted',
                'detection_method': 'timeout_error'
            }
        except Exception as e:
            logger.error(f"Error checking stock: {e}")
            # Try to restart driver on errors
            try:
                self.close()
            except:
                pass
            return {
                'timestamp': datetime.now().isoformat(),
                'url': url,
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
        # Log page title for debugging
        try:
            page_title = self.driver.title
            logger.debug(f"Page title: {page_title}")
        except:
            pass

        # Method 1: Look for "Add to Cart" or "Buy Now" button
        try:
            add_to_cart_selectors = [
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'buy now')]",
                "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')]",
                "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'buy now')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to bag')]",
                "//*[@id='add-to-cart']",
                "//button[contains(@class, 'add-to-cart')]",
                "//button[contains(@class, 'buy-button')]"
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

        # Method 2: Look for "Out of Stock" or similar text (case-insensitive)
        try:
            out_of_stock_selectors = [
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'out of stock')]",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sold out')]",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'not available')]",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'currently unavailable')]",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'notify me')]",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'coming soon')]",
                "//button[@disabled]",
                "//button[contains(@class, 'sold-out')]",
                "//button[contains(@class, 'soldout')]"
            ]

            for selector in out_of_stock_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            element_text = element.text.strip()
                            if element_text:  # Only if there's actual text
                                logger.info(f"Found out of stock indicator: {element_text}")
                                return {
                                    'in_stock': False,
                                    'text': element_text,
                                    'method': 'out_of_stock_text'
                                }
                except NoSuchElementException:
                    continue
        except Exception as e:
            logger.debug(f"Error in out of stock detection: {e}")

        # Method 3: Look for "In Stock" text (case-insensitive)
        try:
            in_stock_selectors = [
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'in stock')]",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'available now')]",
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

        # Method 4: Check page source for keywords
        try:
            page_text = self.driver.page_source.lower()
            logger.debug("Checking page source for stock keywords")

            # Check for common stock indicators in page source
            if 'out of stock' in page_text or 'sold out' in page_text or 'notify me' in page_text or 'coming soon' in page_text:
                return {
                    'in_stock': False,
                    'text': 'Out of stock (detected in page source)',
                    'method': 'page_source'
                }

            if 'add to cart' in page_text or 'buy now' in page_text or 'add to bag' in page_text:
                # Look for disabled state
                if 'disabled' in page_text or 'button disabled' in page_text:
                    return {
                        'in_stock': False,
                        'text': 'Button found but disabled (likely out of stock)',
                        'method': 'page_source_disabled'
                    }
                return {
                    'in_stock': True,
                    'text': 'Possibly in stock (detected in page source)',
                    'method': 'page_source'
                }
        except Exception as e:
            logger.debug(f"Error checking page source: {e}")

        # Save screenshot for debugging and log more info
        try:
            screenshot_path = f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            self.driver.save_screenshot(screenshot_path)
            logger.warning(f"Unable to determine status - Screenshot saved to {screenshot_path}")

            # Log page title and URL for debugging
            logger.warning(f"Current URL: {self.driver.current_url}")
            logger.warning(f"Page title: {self.driver.title}")

            # Log a snippet of visible text
            try:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text[:500]
                logger.debug(f"Page text (first 500 chars): {body_text}")
            except:
                pass

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
        logger.info(f"Monitoring {len(self.urls)} URL(s)")

        try:
            while True:
                check_count += 1
                logger.info(f"Check #{check_count}")

                # Check each URL
                for url in self.urls:
                    # Determine site name for notifications
                    if 'bestbuy.com' in url:
                        site_name = 'Best Buy'
                    elif 'nvidia.com' in url:
                        site_name = 'NVIDIA'
                    else:
                        site_name = 'Unknown Site'

                    result = self.check_stock(url)

                    if result['in_stock'] is True:
                        logger.warning(f"PRODUCT IS IN STOCK AT {site_name.upper()}!")
                        alert_message = f"""
🚨 RTX 5090 IS IN STOCK at {site_name}! 🚨

Status: {result['status_text']}
Store: {site_name}
Time: {result['timestamp']}

👉 BUY NOW:
{result['url']}

Click the link above to purchase immediately!
"""
                        print("\n" + "="*60)
                        print(f"ALERT: RTX 5090 IS IN STOCK at {site_name}!")
                        print(f"Status: {result['status_text']}")
                        print(f"URL: {result['url']}")
                        print(f"Time: {result['timestamp']}")
                        print("="*60 + "\n")

                        # Send notifications
                        if self.notifier:
                            self.notifier.notify(
                                message=alert_message,
                                title=f"RTX 5090 IN STOCK at {site_name}!"
                            )

                    elif result['in_stock'] is False:
                        logger.info(f"{site_name}: Out of stock - {result['status_text']}")
                    else:
                        logger.warning(f"{site_name}: Unclear status - {result['status_text']}")

                    # Small delay between checking different sites (1-3 seconds)
                    if url != self.urls[-1]:  # Not the last URL
                        time.sleep(random.uniform(1.0, 3.0))

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
        action='append',
        default=None,
        help='URL to check (can be specified multiple times for multiple sites)'
    )
    parser.add_argument(
        '--no-nvidia',
        action='store_true',
        help='Exclude NVIDIA from default URLs (only monitor Best Buy)'
    )
    parser.add_argument(
        '--no-bestbuy',
        action='store_true',
        help='Exclude Best Buy from default URLs (only monitor NVIDIA)'
    )
    parser.add_argument(
        '--nvidia-url',
        type=str,
        default=None,
        help='Custom NVIDIA URL to monitor (overrides default NVIDIA URL)'
    )
    parser.add_argument(
        '--bestbuy-url',
        type=str,
        default=None,
        help='Custom Best Buy URL to monitor (overrides default Best Buy URL)'
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

    # Set default URLs if none provided
    if args.url is None:
        urls = []

        # Add NVIDIA unless excluded (use custom URL if provided)
        if not args.no_nvidia:
            nvidia_url = args.nvidia_url if args.nvidia_url else 'https://marketplace.nvidia.com/en-us/consumer/graphics-cards/geforce-rtx-5090-founders-edition/'
            urls.append(nvidia_url)

        # Add Best Buy unless excluded (use custom URL if provided, otherwise use latest product URL format)
        if not args.no_bestbuy:
            bestbuy_url = args.bestbuy_url if args.bestbuy_url else 'https://www.bestbuy.com/product/nvidia-geforce-rtx-5090-32gb-gddr7-founders-edition-graphics-card-dark-gun-metal/J3GWYHGPCP'
            urls.append(bestbuy_url)

        # Make sure at least one URL is enabled
        if not urls:
            print("Error: Cannot exclude both NVIDIA and Best Buy. At least one site must be monitored.")
            sys.exit(1)

        # Log which sites are being monitored
        site_names = []
        if not args.no_nvidia:
            site_names.append("NVIDIA")
        if not args.no_bestbuy:
            site_names.append("Best Buy")
        logger.info(f"Monitoring: {' + '.join(site_names)}")
    else:
        urls = args.url

    checker = NvidiaStockChecker(
        urls=urls,
        headless=not args.no_headless,
        notifier=notifier
    )

    try:
        if args.monitor:
            checker.monitor(interval=args.interval, duration=args.duration)
        else:
            # Single check mode - check all URLs
            for url in checker.urls:
                result = checker.check_stock(url)

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
