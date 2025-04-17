from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import random
from dotenv import load_dotenv
import logging
import undetected_chromedriver as uc

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuotexScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        load_dotenv()
        self.email = os.getenv('QUOTEX_EMAIL')
        self.password = os.getenv('QUOTEX_PASSWORD')
        self.proxy = os.getenv('PROXY_SERVER')  # Format: "host:port" or "username:password@host:port"
        logger.info("QuotexScraper initialized")
        
    def setup_driver(self):
        """Set up undetected Chrome WebDriver with anti-detection measures."""
        try:
            logger.info("Setting up undetected Chrome WebDriver...")
            
            # Use undetected-chromedriver to bypass bot detection
            options = uc.ChromeOptions()
            
            # Add proxy if defined
            if self.proxy:
                logger.info(f"Using proxy: {self.proxy}")
                options.add_argument(f'--proxy-server={self.proxy}')
            
            # Add standard options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # Randomize user agent to avoid detection
            user_agents = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0'
            ]
            options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
            # Create undetected Chrome driver
            self.driver = uc.Chrome(options=options)
            
            # Add additional anti-detection measures
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set longer wait time
            self.wait = WebDriverWait(self.driver, 30)
            
            logger.info("Chrome WebDriver setup completed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {str(e)}")
            return False
        
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Add a random delay to mimic human behavior."""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        
    def simulate_human_typing(self, element, text):
        """Type text with random delays between characters to mimic human typing."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))
        
    def move_to_random_elements(self, count=3):
        """Move mouse to random elements on the page to simulate human behavior."""
        try:
            elements = self.driver.find_elements(By.TAG_NAME, "div")
            if len(elements) > count:
                random_elements = random.sample(elements, min(count, len(elements)))
                for element in random_elements:
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                        time.sleep(random.uniform(0.3, 0.7))
                    except:
                        pass
        except:
            pass
        
    def login(self):
        """Log in to Quotex."""
        try:
            logger.info("Attempting to login to Quotex...")
            # First navigate to the homepage
            self.driver.get('https://quotex.com/')
            logger.info("Navigated to homepage")
            self.random_delay(3, 5)
            
            # Take screenshot for debugging
            self.driver.save_screenshot('homepage.png')
            logger.info("Saved homepage screenshot")
            
            # Navigate directly to login page instead of clicking login link
            logger.info("Navigating directly to login page")
            self.driver.get('https://quotex.com/sign-in')
            self.random_delay(5, 7)
            
            # Take screenshot for debugging
            self.driver.save_screenshot('login_page.png')
            logger.info("Saved login page screenshot")
            
            # Print page source for debugging
            logger.info(f"Page title: {self.driver.title}")
            
            # Check for Cloudflare challenge
            if "Just a moment" in self.driver.title or "Checking your browser" in self.driver.page_source:
                logger.info("Detected Cloudflare challenge, waiting for it to resolve...")
                # Wait longer for Cloudflare to resolve
                time.sleep(15)
                self.driver.save_screenshot('after_cloudflare.png')
                logger.info(f"Page title after waiting: {self.driver.title}")
            
            # Try different ways to find the email field
            email_field = None
            try:
                logger.info("Waiting for login form elements to be interactive...")
                # Wait for any input field to be visible first
                self.wait.until(EC.visibility_of_element_located((By.TAG_NAME, "input")))
                self.random_delay(2, 3)
                
                # Try by name with explicit wait for visibility
                email_field = self.wait.until(
                    EC.element_to_be_clickable((By.NAME, 'email'))
                )
                logger.info("Found email field by NAME")
            except Exception as e1:
                logger.warning(f"Could not find email field by name: {str(e1)}")
                try:
                    # Try by ID
                    email_field = self.wait.until(
                        EC.element_to_be_clickable((By.ID, 'email'))
                    )
                    logger.info("Found email field by ID")
                except Exception as e2:
                    logger.warning(f"Could not find email field by ID: {str(e2)}")
                    try:
                        # Try by XPath with more specific targeting
                        email_field = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, "//input[@type='email' or @placeholder='Email' or contains(@name, 'email')]"))
                        )
                        logger.info("Found email field by XPath")
                    except Exception as e3:
                        # Try any input field as a last resort
                        try:
                            inputs = self.driver.find_elements(By.TAG_NAME, "input")
                            if inputs:
                                # Ensure element is scrolled into view
                                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", inputs[0])
                                self.random_delay(1, 2)
                                email_field = inputs[0]
                                logger.info("Found email field as first input")
                        except:
                            logger.error("All attempts to find email field failed")
                            return False
            
            if not email_field:
                logger.error("Email field not found")
                return False
            
            # Ensure element is scrolled into view
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", email_field)
            self.random_delay(1, 2)
                
            # Clear the field and enter email with human-like typing
            email_field.clear()
            self.simulate_human_typing(email_field, self.email)
            logger.info("Email entered")
            self.random_delay(1, 2)
            
            # Save screenshot after email entry
            self.driver.save_screenshot('after_email.png')
            
            # Try different ways to find the password field
            password_field = None
            try:
                # Try by name
                password_field = self.wait.until(
                    EC.element_to_be_clickable((By.NAME, 'password'))
                )
                logger.info("Found password field by NAME")
            except Exception as e1:
                logger.warning(f"Could not find password field by name: {str(e1)}")
                try:
                    # Try by ID
                    password_field = self.wait.until(
                        EC.element_to_be_clickable((By.ID, 'password'))
                    )
                    logger.info("Found password field by ID")
                except Exception as e2:
                    logger.warning(f"Could not find password field by ID: {str(e2)}")
                    try:
                        # Try by XPath with more specific targeting
                        password_field = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, "//input[@type='password' or contains(@name, 'password')]"))
                        )
                        logger.info("Found password field by XPath")
                    except Exception as e3:
                        # Try by input position as last resort
                        try:
                            inputs = self.driver.find_elements(By.TAG_NAME, "input")
                            if len(inputs) > 1:
                                # Ensure element is scrolled into view
                                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", inputs[1])
                                self.random_delay(1, 2)
                                password_field = inputs[1]  # Assuming it's the second input
                                logger.info("Found password field as second input")
                        except:
                            logger.error("All attempts to find password field failed")
                            return False
            
            if not password_field:
                logger.error("Password field not found")
                return False
            
            # Ensure element is scrolled into view
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", password_field)
            self.random_delay(1, 2)
                
            # Clear the field and enter password with human-like typing
            password_field.clear()
            self.simulate_human_typing(password_field, self.password)
            logger.info("Password entered")
            self.random_delay(1, 2)
            
            # Take screenshot before clicking login
            self.driver.save_screenshot('before_login_click.png')
            
            # Try different ways to find the login button
            login_button = None
            try:
                # Try by type=submit
                login_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
                )
                logger.info("Found login button by type=submit")
            except Exception as e1:
                logger.warning(f"Could not find login button by type=submit: {str(e1)}")
                try:
                    # Try by text
                    login_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log') or contains(text(), 'Sign') or contains(text(), 'Enter')]"))
                    )
                    logger.info("Found login button by text")
                except Exception as e2:
                    logger.warning(f"Could not find login button by text: {str(e2)}")
                    try:
                        # Try by any button
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        if buttons:
                            # Ensure element is scrolled into view
                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", buttons[0])
                            self.random_delay(1, 2)
                            login_button = buttons[0]  # Assume first button is login
                            logger.info("Found login button as first button")
                        else:
                            # Last resort - try div or a tag that might be a button
                            possible_button = self.wait.until(
                                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'button') or contains(@class, 'btn')] | //a[contains(@class, 'button') or contains(@class, 'btn')]"))
                            )
                            login_button = possible_button
                            logger.info("Found login button as div/a with button class")
                    except Exception as e3:
                        logger.error(f"All attempts to find login button failed: {str(e3)}")
                        return False
            
            if not login_button:
                logger.error("Login button not found")
                return False
            
            # Ensure element is scrolled into view
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", login_button)
            self.random_delay(1, 2)
                
            # Click login button using JavaScript
            try:
                self.driver.execute_script("arguments[0].click();", login_button)
                logger.info("Login button clicked with JavaScript")
            except Exception as e:
                logger.warning(f"JavaScript click failed: {str(e)}, trying normal click")
                login_button.click()
                logger.info("Login button clicked normally")
            
            # Wait for login to complete with a longer timeout
            self.random_delay(10, 15)
            
            # Take screenshot after login attempt
            self.driver.save_screenshot('after_login.png')
            logger.info("Saved after login screenshot")
            
            # Check if login was successful by looking for balance or other indicators
            try:
                # Try a few different selectors that might indicate successful login
                try:
                    balance_element = self.wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'balance'))
                    )
                    logger.info("Login verified by finding balance element")
                    return True
                except:
                    logger.warning("Could not find balance element")
                    
                    try:
                        # Look for any element that might indicate logged-in state
                        profile_element = self.wait.until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'profile') or contains(@class, 'account')]"))
                        )
                        logger.info("Login verified by finding profile element")
                        return True
                    except:
                        logger.warning("Could not find profile element")
                        
                        # Look for trading platform elements
                        try:
                            platform_element = self.wait.until(
                                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'chart') or contains(@class, 'trading')]"))
                            )
                            logger.info("Login verified by finding trading platform element")
                            return True
                        except:
                            logger.warning("Could not find trading platform element")
                            
                            # As a last resort, check if we're redirected away from login page
                            current_url = self.driver.current_url
                            logger.info(f"Current URL after login attempt: {current_url}")
                            if '/login' not in current_url:
                                logger.info("Login verified by URL change")
                                return True
                            else:
                                logger.error("Still on login page - login failed")
                                return False
            except Exception as e:
                logger.error(f"Login verification failed: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
            
    def get_balance(self):
        """Get current account balance."""
        try:
            logger.info("Attempting to get balance...")
            # Take screenshot for debugging
            self.driver.save_screenshot('balance_check.png')
            
            # Wait for balance element to be visible
            try:
                balance_element = self.wait.until(
                    EC.visibility_of_element_located((By.CLASS_NAME, 'balance'))
                )
                balance = balance_element.text
                logger.info(f"Balance retrieved by class: {balance}")
                return balance
            except Exception as e:
                logger.warning(f"Failed to get balance by class: {str(e)}")
                try:
                    # Try alternate XPath
                    balance_element = self.wait.until(
                        EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'balance') or contains(text(), '$')]"))
                    )
                    balance = balance_element.text
                    logger.info(f"Balance retrieved by XPath: {balance}")
                    return balance
                except Exception as e2:
                    logger.error(f"All attempts to get balance failed: {str(e2)}")
                    return None
        except Exception as e:
            logger.error(f"Failed to get balance: {str(e)}")
            return None
            
    def place_trade(self, asset, direction, amount):
        """Place a trade on the specified asset."""
        try:
            logger.info(f"Attempting to place {direction} trade for {asset} with amount {amount}")
            # Navigate to trading page
            self.driver.get(f'https://quotex.com/trading/{asset}')
            logger.info(f"Navigated to trading page for {asset}")
            self.random_delay(5, 8)
            
            # Take screenshot for debugging
            self.driver.save_screenshot('trading_page.png')
            
            # Select direction (call/put)
            logger.info(f"Looking for {direction} button...")
            try:
                if direction.lower() in ['call', 'up']:
                    direction_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'up') or contains(@class, 'call') or contains(text(), 'Up') or contains(text(), 'Call')]"))
                    )
                else:  # down or put
                    direction_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'down') or contains(@class, 'put') or contains(text(), 'Down') or contains(text(), 'Put')]"))
                    )
                direction_button.click()
                logger.info(f"{direction} button clicked")
                self.random_delay(1, 2)
            except Exception as e:
                logger.error(f"Failed to click {direction} button: {str(e)}")
                return False
            
            # Set amount
            logger.info("Looking for amount field...")
            try:
                # Try different ways to find amount field
                try:
                    amount_field = self.wait.until(
                        EC.presence_of_element_located((By.NAME, 'amount'))
                    )
                except:
                    try:
                        amount_field = self.wait.until(
                            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Amount' or @type='number']"))
                        )
                    except:
                        amount_field = self.wait.until(
                            EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'amount')]"))
                        )
                
                amount_field.clear()
                self.simulate_human_typing(amount_field, str(amount))
                logger.info(f"Amount set to {amount}")
                self.random_delay(1, 2)
            except Exception as e:
                logger.error(f"Failed to set amount: {str(e)}")
                return False
            
            # Place trade
            logger.info("Looking for trade button...")
            try:
                trade_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Place Trade') or contains(text(), 'Trade Now') or contains(@class, 'trade')]"))
                )
                trade_button.click()
                logger.info("Trade button clicked")
                self.random_delay(1, 2)
            except Exception as e:
                logger.error(f"Failed to click trade button: {str(e)}")
                return False
            
            # Wait for trade confirmation
            self.random_delay(3, 5)
            self.driver.save_screenshot('after_trade.png')
            
            return True
        except Exception as e:
            logger.error(f"Failed to place trade: {str(e)}")
            return False
            
    def close(self):
        """Close the browser."""
        if self.driver:
            logger.info("Closing browser...")
            self.driver.quit()
            logger.info("Browser closed")
            
    def __enter__(self):
        self.setup_driver()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 