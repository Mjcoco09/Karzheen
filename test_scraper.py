from quotex_scraper import QuotexScraper
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Quotex scraper test...")
    
    # Initialize the scraper
    with QuotexScraper() as scraper:
        # Setup the driver
        if not scraper.setup_driver():
            logger.error("Failed to set up WebDriver")
            return
            
        # Login to Quotex
        if not scraper.login():
            logger.error("Failed to login to Quotex")
            return
            
        logger.info("Successfully logged in")
        
        # Get balance
        balance = scraper.get_balance()
        logger.info(f"Current balance: {balance}")
        
        # Take some time to observe the page
        time.sleep(10)
        
        logger.info("Test completed")

if __name__ == "__main__":
    main() 