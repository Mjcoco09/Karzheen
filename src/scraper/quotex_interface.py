import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config.credentials import Credentials
from .selenium_manager import SeleniumManager

logger = logging.getLogger(__name__)

class QuotexInterface:
    def __init__(self, headless=True):
        self.selenium = SeleniumManager(headless=headless)
        self.credentials = Credentials.get_quotex_credentials()
        self.is_logged_in = False
        self.is_demo_mode = False

    def login(self):
        """Login to Quotex platform."""
        try:
            if not self.selenium.setup_driver():
                return False

            # Navigate to Quotex login page
            self.selenium.driver.get("https://quotex.com/login")
            self.selenium.random_delay()

            # Handle cookie consent if present
            try:
                cookie_button = self.selenium.wait_for_element(
                    By.XPATH, "//button[contains(text(), 'Accept')]"
                )
                if cookie_button:
                    cookie_button.click()
                    self.selenium.random_delay()
            except:
                pass

            # Enter email
            if not self.selenium.send_keys(
                By.NAME, "email", self.credentials['email']
            ):
                return False

            # Enter password
            if not self.selenium.send_keys(
                By.NAME, "password", self.credentials['password']
            ):
                return False

            # Click login button
            if not self.selenium.click_element(
                By.XPATH, "//button[contains(text(), 'Login')]"
            ):
                return False

            # Wait for login to complete
            try:
                WebDriverWait(self.selenium.driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "balance"))
                )
                self.is_logged_in = True
                logger.info("Successfully logged in to Quotex")
                return True
            except TimeoutException:
                logger.error("Login timeout - could not verify successful login")
                return False

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def switch_to_demo(self):
        """Switch to demo account mode."""
        try:
            if not self.is_logged_in:
                logger.error("Must be logged in to switch to demo mode")
                return False

            # Click on balance to open account switcher
            if not self.selenium.click_element(By.CLASS_NAME, "balance"):
                return False

            # Click demo account button
            if not self.selenium.click_element(
                By.XPATH, "//div[contains(text(), 'Demo')]"
            ):
                return False

            self.is_demo_mode = True
            logger.info("Switched to demo account")
            return True

        except Exception as e:
            logger.error(f"Failed to switch to demo mode: {str(e)}")
            return False

    def get_balance(self):
        """Get current account balance."""
        try:
            if not self.is_logged_in:
                logger.error("Must be logged in to get balance")
                return None

            balance_text = self.selenium.get_element_text(By.CLASS_NAME, "balance")
            if balance_text:
                # Extract numeric value from balance text
                balance = float(balance_text.replace('$', '').replace(',', ''))
                return balance
            return None

        except Exception as e:
            logger.error(f"Failed to get balance: {str(e)}")
            return None

    def select_asset(self, asset_name):
        """Select trading asset."""
        try:
            if not self.is_logged_in:
                logger.error("Must be logged in to select asset")
                return False

            # Click on asset selector
            if not self.selenium.click_element(
                By.XPATH, "//div[contains(@class, 'asset-selector')]"
            ):
                return False

            # Search for asset
            if not self.selenium.send_keys(
                By.XPATH, "//input[@placeholder='Search']", asset_name
            ):
                return False

            # Select asset from results
            if not self.selenium.click_element(
                By.XPATH, f"//div[contains(text(), '{asset_name}')]"
            ):
                return False

            logger.info(f"Selected asset: {asset_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to select asset {asset_name}: {str(e)}")
            return False

    def place_trade(self, direction, amount):
        """Place a trade in the specified direction."""
        try:
            if not self.is_logged_in:
                logger.error("Must be logged in to place trade")
                return False

            # Click on trade amount input
            if not self.selenium.click_element(
                By.XPATH, "//input[@placeholder='Amount']"
            ):
                return False

            # Enter trade amount
            if not self.selenium.send_keys(
                By.XPATH, "//input[@placeholder='Amount']", str(amount)
            ):
                return False

            # Click trade button based on direction
            if direction.lower() == 'up':
                if not self.selenium.click_element(
                    By.XPATH, "//button[contains(@class, 'up')]"
                ):
                    return False
            elif direction.lower() == 'down':
                if not self.selenium.click_element(
                    By.XPATH, "//button[contains(@class, 'down')]"
                ):
                    return False
            else:
                logger.error(f"Invalid trade direction: {direction}")
                return False

            logger.info(f"Placed {direction} trade for ${amount}")
            return True

        except Exception as e:
            logger.error(f"Failed to place trade: {str(e)}")
            return False

    def close(self):
        """Close the Quotex interface."""
        self.selenium.close()
        self.is_logged_in = False
        self.is_demo_mode = False 