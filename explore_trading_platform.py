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

# Create screenshots directory
screenshots_dir = 'screenshots'
os.makedirs(screenshots_dir, exist_ok=True)

def take_screenshot(driver, filename):
    """Take a screenshot and save it to the screenshots directory."""
    filepath = os.path.join(screenshots_dir, filename)
    try:
        driver.save_screenshot(filepath)
        logger.info(f"Screenshot saved as {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        return False

def find_elements_by_class_or_tag(driver, class_names, tag_names):
    """Find elements by class name or tag name and log their attributes."""
    results = []
    
    # Search by class name
    for class_name in class_names:
        try:
            elements = driver.find_elements(By.CLASS_NAME, class_name)
            if elements:
                logger.info(f"Found {len(elements)} elements with class '{class_name}'")
                for i, element in enumerate(elements[:5]):  # Limit to first 5 elements
                    try:
                        element_text = element.text
                        element_html = element.get_attribute('outerHTML')
                        logger.info(f"Element {i} with class '{class_name}' - Text: {element_text[:50]}")
                        results.append((element, class_name))
                    except:
                        pass
        except Exception as e:
            logger.error(f"Error finding elements by class '{class_name}': {e}")
    
    # Search by tag name
    for tag_name in tag_names:
        try:
            elements = driver.find_elements(By.TAG_NAME, tag_name)
            if elements:
                logger.info(f"Found {len(elements)} elements with tag '{tag_name}'")
                for i, element in enumerate(elements[:5]):  # Limit to first 5 elements
                    try:
                        element_text = element.text
                        if element_text.strip():  # Only log if there's actual text
                            logger.info(f"Element {i} with tag '{tag_name}' - Text: {element_text[:50]}")
                            results.append((element, tag_name))
                    except:
                        pass
        except Exception as e:
            logger.error(f"Error finding elements by tag '{tag_name}': {e}")
    
    return results

def find_trade_interface_elements(driver):
    """Try to find key elements of the trading interface."""
    try:
        # Take a screenshot of the current state
        take_screenshot(driver, "trading_interface.png")
        
        # Look for various trading-related elements
        logger.info("Searching for trading interface elements...")
        
        # Classes that might contain balance or trading info
        classes_to_check = [
            'balance', 'account-balance', 'wallet', 'amount', 'price',
            'asset', 'currency-pair', 'chart', 'trade-button', 'trading-button',
            'up', 'down', 'buy', 'sell', 'trade-amount', 'time-frame',
            'header', 'sidebar', 'menu', 'profile', 'account'
        ]
        
        # Tags to check for text content
        tags_to_check = ['div', 'span', 'button', 'h1', 'h2', 'h3', 'p', 'a']
        
        # Find elements
        found_elements = find_elements_by_class_or_tag(driver, classes_to_check, [])
        
        # Try to find specific trading elements by looking for text patterns
        try:
            # Find buttons with "Up" or "Down" text (or similar)
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                button_text = button.text.lower()
                if any(term in button_text for term in ['up', 'down', 'buy', 'sell', 'call', 'put']):
                    logger.info(f"Found trading button: {button_text}")
                    # Highlight the element and take a screenshot
                    driver.execute_script("arguments[0].style.border='3px solid red'", button)
                    take_screenshot(driver, f"trade_button_{button_text}.png")
        except Exception as e:
            logger.error(f"Error finding trade buttons: {e}")
        
        # Try to find amount input field
        try:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for input_field in inputs:
                input_type = input_field.get_attribute('type')
                input_placeholder = input_field.get_attribute('placeholder')
                input_name = input_field.get_attribute('name')
                logger.info(f"Found input field - Type: {input_type}, Name: {input_name}, Placeholder: {input_placeholder}")
                
                # Highlight the element and take a screenshot
                driver.execute_script("arguments[0].style.border='3px solid blue'", input_field)
                input_id = input_name or input_placeholder or input_type
                take_screenshot(driver, f"input_field_{input_id}.png")
        except Exception as e:
            logger.error(f"Error finding input fields: {e}")
        
        # Look for the main chart element
        try:
            chart_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'chart') or contains(@id, 'chart')]")
            if chart_elements:
                logger.info(f"Found chart element")
                driver.execute_script("arguments[0].style.border='3px solid green'", chart_elements[0])
                take_screenshot(driver, "chart_element.png")
        except Exception as e:
            logger.error(f"Error finding chart element: {e}")
        
        return True
    except Exception as e:
        logger.error(f"Error exploring trading interface: {e}")
        return False

def main():
    logger.info("Starting exploration of Quotex trading platform...")
    
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
        
        # Take a screenshot of the initial state
        take_screenshot(driver, "initial_state.png")
        
        # Explore the trading interface
        find_trade_interface_elements(driver)
        
        # Try to get page HTML source
        try:
            with open(os.path.join(screenshots_dir, 'page_source.html'), 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logger.info("Saved page source")
        except Exception as e:
            logger.error(f"Error saving page source: {e}")
        
        # Keep the browser open for a while 
        logger.info("Keeping browser open for 10 seconds...")
        time.sleep(10)
        
        # Close the browser
        logger.info("Closing browser...")
        driver.quit()
        logger.info("Browser closed. Check the screenshots directory for results.")
        
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main() 