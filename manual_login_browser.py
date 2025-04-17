import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a persistent profile directory
home_dir = str(Path.home())
profile_dir = os.path.join(home_dir, 'quotex_chrome_profile')
os.makedirs(profile_dir, exist_ok=True)
print(f"Profile directory: {profile_dir}")

# Get login credentials from environment variables
email = os.getenv('QUOTEX_EMAIL')
password = os.getenv('QUOTEX_PASSWORD')
print(f"Using email: {email}")

def main():
    print("Starting manual login session...")
    
    # Configure Chrome options with persistent profile
    options = uc.ChromeOptions()
    options.add_argument(f'--user-data-dir={profile_dir}')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-dev-shm-usage')
    
    # Launch browser
    print("Launching browser...")
    driver = uc.Chrome(options=options)
    
    # Navigate to login page
    driver.get('https://quotex.com/sign-in')
    print("Please log in manually now...")
    print(f"Email: {email}")
    print(f"Password: {password}")
    
    # Keep the browser open for manual interaction
    print("\nThe browser will remain open for you to manually log in.")
    print("After you've successfully logged in, the session cookies will be saved to the profile.")
    print("Press Ctrl+C in the terminal to close the browser when you're done.")
    
    try:
        # Keep the browser open until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nClosing browser...")
        driver.quit()
        print("Browser closed. Your session has been saved.")

if __name__ == "__main__":
    main() 