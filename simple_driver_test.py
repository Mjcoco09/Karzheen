import undetected_chromedriver as uc
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

def test_driver():
    """Test undetected_chromedriver functionality."""
    logger.info("Starting WebDriver test...")
    
    try:
        # Create options
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        # Create Chrome driver
        logger.info("Creating undetected chromedriver...")
        driver = uc.Chrome(options=options)
        
        # Open a simple site
        logger.info("Opening Google...")
        driver.get('https://www.google.com')
        
        # Take a screenshot
        logger.info("Taking screenshot...")
        driver.save_screenshot('google_test.png')
        
        # Wait a bit to see the page
        time.sleep(5)
        
        # Get the title
        title = driver.title
        logger.info(f"Page title: {title}")
        
        # Close driver
        driver.quit()
        logger.info("Driver closed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error testing driver: {e}")
        return False

if __name__ == "__main__":
    if test_driver():
        logger.info("WebDriver test completed successfully!")
    else:
        logger.error("WebDriver test failed") 