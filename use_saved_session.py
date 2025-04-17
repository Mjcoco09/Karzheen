import os
import time
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Use the same profile directory
home_dir = str(Path.home())
profile_dir = os.path.join(home_dir, 'quotex_chrome_profile')

def check_login_status(driver):
    """Check if we're logged in to Quotex."""
    try:
        # Take screenshot to see current state
        driver.save_screenshot('current_state.png')
        logger.info(f"Current URL: {driver.current_url}")
        
        # Check for elements that would indicate logged in state
        try:
            # Try to find balance element (typically visible when logged in)
            balance = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'balance'))
            )
            logger.info(f"Found balance element: {balance.text}")
            return True
        except:
            logger.info("Balance element not found")
            
        # Check URL - if we're not on the login page, we might be logged in
        if '/sign-in' not in driver.current_url and '/login' not in driver.current_url:
            logger.info("Not on login page, may be logged in")
            return True
            
        return False
    
    except Exception as e:
        logger.error(f"Error checking login status: {e}")
        return False

def get_balance(driver):
    """Get current account balance."""
    try:
        balance_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'balance'))
        )
        balance = balance_element.text
        logger.info(f"Balance: {balance}")
        return balance
    except Exception as e:
        logger.error(f"Error getting balance: {e}")
        return None

def take_screenshot(driver, filename="screenshot.png"):
    """Take a screenshot."""
    try:
        driver.save_screenshot(filename)
        logger.info(f"Screenshot saved as {filename}")
        return True
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        return False

def main():
    logger.info("Starting Quotex session with saved profile...")
    
    # Configure Chrome options with persistent profile
    options = uc.ChromeOptions()
    options.add_argument(f'--user-data-dir={profile_dir}')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        # Launch browser
        logger.info("Launching browser...")
        driver = uc.Chrome(options=options)
        
        # Navigate to Quotex
        driver.get('https://quotex.com/')
        logger.info("Navigated to Quotex homepage")
        
        # Wait for page to load
        time.sleep(5)
        
        # Check if we're logged in
        if check_login_status(driver):
            logger.info("Successfully logged in with saved session")
            take_screenshot(driver, "logged_in.png")
            
            # Get balance
            balance = get_balance(driver)
            if balance:
                logger.info(f"Current balance: {balance}")
            
            # Add more automated actions here
            
        else:
            logger.error("Not logged in. Please run manual_login_browser.py first")
            driver.get('https://quotex.com/sign-in')
            logger.info("Redirected to login page")
            take_screenshot(driver, "not_logged_in.png")
        
        # Keep the browser open for a while to see the results
        time.sleep(10)
        
        # Close the browser
        logger.info("Closing browser...")
        driver.quit()
        logger.info("Browser closed")
        
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main() 