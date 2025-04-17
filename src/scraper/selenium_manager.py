import logging
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from config.config import SELENIUM_CONFIG

logger = logging.getLogger(__name__)

class SeleniumManager:
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
        self.timeout = SELENIUM_CONFIG['TIMEOUT']
        self.user_agent = SELENIUM_CONFIG['USER_AGENT']

    def setup_driver(self):
        """Initialize the Chrome WebDriver with configured options."""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            
            chrome_options.add_argument(f'user-agent={self.user_agent}')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Add additional options to avoid detection
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute CDP commands to avoid detection
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": self.user_agent})
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })

            logger.info("Chrome WebDriver initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
            return False

    def random_delay(self, min_seconds=2, max_seconds=5):
        """Add a random delay between actions to avoid detection."""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def wait_for_element(self, by, value, timeout=None):
        """Wait for an element to be present and visible."""
        if timeout is None:
            timeout = self.timeout
        
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.error(f"Timeout waiting for element: {value}")
            return None

    def click_element(self, by, value, timeout=None):
        """Click an element with error handling."""
        try:
            element = self.wait_for_element(by, value, timeout)
            if element:
                self.random_delay()
                element.click()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to click element {value}: {str(e)}")
            return False

    def send_keys(self, by, value, text, timeout=None):
        """Send keys to an element with error handling."""
        try:
            element = self.wait_for_element(by, value, timeout)
            if element:
                self.random_delay()
                element.clear()
                element.send_keys(text)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to send keys to element {value}: {str(e)}")
            return False

    def get_element_text(self, by, value, timeout=None):
        """Get text from an element with error handling."""
        try:
            element = self.wait_for_element(by, value, timeout)
            if element:
                return element.text
            return None
        except Exception as e:
            logger.error(f"Failed to get text from element {value}: {str(e)}")
            return None

    def take_screenshot(self, filename):
        """Take a screenshot of the current page."""
        try:
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved as {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            return False

    def close(self):
        """Close the WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {str(e)}") 