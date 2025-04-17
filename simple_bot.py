#!/usr/bin/env python3
import os
import time
import json
import logging
import requests
from dotenv import load_dotenv
from quotex_scraper import QuotexScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get the bot token from environment variable
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_USER_IDS = [int(id) for id in os.getenv('ADMIN_USER_IDS').split(',') if id.strip()]

# Initialize global QuotexScraper
scraper = None

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}/"
        self.last_update_id = 0
        self.commands = {
            '/start': self.start_command,
            '/help': self.help_command,
            '/status': self.status_command,
            '/balance': self.balance_command,
            '/trade': self.trade_command,
            '/stop': self.stop_command
        }

    def get_updates(self):
        """Get updates from Telegram."""
        try:
            params = {'offset': self.last_update_id + 1, 'timeout': 30}
            response = requests.get(self.api_url + 'getUpdates', params=params)
            data = response.json()
            
            if data.get('ok') and data.get('result'):
                self.last_update_id = max(update['update_id'] for update in data['result']) if data['result'] else self.last_update_id
                return data['result']
            return []
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []

    def send_message(self, chat_id, text):
        """Send message to a chat."""
        try:
            params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
            response = requests.post(self.api_url + 'sendMessage', params=params)
            return response.json()
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None

    def process_updates(self, updates):
        """Process updates from Telegram."""
        for update in updates:
            if 'message' in update and 'text' in update['message']:
                message = update['message']
                chat_id = message['chat']['id']
                user_id = message['from']['id']
                text = message['text']
                
                # Check if it's a command
                if text.startswith('/'):
                    # Split into command and arguments
                    command_parts = text.split()
                    command = command_parts[0].lower()
                    args = command_parts[1:] if len(command_parts) > 1 else []
                    
                    # Process command if it exists
                    if command in self.commands:
                        logger.info(f"Received command {command} from user {user_id}")
                        self.commands[command](chat_id, user_id, args)
                    else:
                        self.send_message(chat_id, "Unknown command. Use /help to see available commands.")

    def check_admin(self, chat_id, user_id):
        """Check if the user is an admin."""
        is_admin = user_id in ADMIN_USER_IDS
        logger.info(f"Admin check for user {user_id}: {is_admin}")
        
        if not is_admin:
            self.send_message(chat_id, "Sorry, you are not authorized to use this bot.")
        
        return is_admin

    def start_command(self, chat_id, user_id, args):
        """Handle /start command."""
        global scraper
        
        if not self.check_admin(chat_id, user_id):
            return
            
        try:
            self.send_message(chat_id, "Connecting to Quotex... This may take a moment.")
            
            # Initialize the scraper
            scraper = QuotexScraper()
            
            # Setup the driver
            setup_success = scraper.setup_driver()
            if not setup_success:
                self.send_message(chat_id, "❌ Failed to setup Chrome driver. Please check logs for details.")
                return
                
            # Login to Quotex
            login_success = scraper.login()
            if login_success:
                logger.info("Successfully connected to Quotex")
                self.send_message(chat_id, '✅ Bot is connected to Quotex! Use /help to see available commands.')
            else:
                logger.error("Failed to connect to Quotex")
                self.send_message(chat_id, '❌ Failed to connect to Quotex. Please check the logs and try again later.')
        except Exception as e:
            logger.error(f"Error in start command: {str(e)}")
            self.send_message(chat_id, f'❌ Error: {str(e)}')
            
            # Clean up any incomplete setup
            if scraper and scraper.driver:
                try:
                    scraper.close()
                except:
                    pass

    def help_command(self, chat_id, user_id, args):
        """Handle /help command."""
        if not self.check_admin(chat_id, user_id):
            return
            
        help_text = """
Available commands:
/start - Connect to Quotex
/help - Show this help message
/status - Check trading status
/balance - Check account balance
/trade [asset] [direction] [amount] - Execute a trade (e.g., /trade EURUSD call 1.0)
/stop - Stop and close connection
        """
        self.send_message(chat_id, help_text)

    def status_command(self, chat_id, user_id, args):
        """Handle /status command."""
        if not self.check_admin(chat_id, user_id):
            return
            
        try:
            if scraper and scraper.driver:
                status_text = "✅ Bot is connected and running"
            else:
                status_text = "❌ Bot is not connected. Use /start to reconnect."
            
            logger.info(f"Status: {status_text}")
            self.send_message(chat_id, status_text)
        except Exception as e:
            logger.error(f"Error checking status: {str(e)}")
            self.send_message(chat_id, f"Error checking status: {str(e)}")

    def balance_command(self, chat_id, user_id, args):
        """Handle /balance command."""
        if not self.check_admin(chat_id, user_id):
            return
            
        try:
            if not scraper or not scraper.driver:
                self.send_message(chat_id, "❌ Not connected to Quotex. Use /start to reconnect.")
                return
                
            balance = scraper.get_balance()
            if balance:
                logger.info(f"Balance retrieved: {balance}")
                self.send_message(chat_id, f"💰 Current balance: ${balance}")
            else:
                logger.error("Failed to get balance")
                self.send_message(chat_id, "❌ Failed to get balance")
        except Exception as e:
            logger.error(f"Error checking balance: {str(e)}")
            self.send_message(chat_id, f"Error checking balance: {str(e)}")

    def trade_command(self, chat_id, user_id, args):
        """Handle /trade command."""
        if not self.check_admin(chat_id, user_id):
            return
            
        try:
            if not scraper or not scraper.driver:
                self.send_message(chat_id, "❌ Not connected to Quotex. Use /start to reconnect.")
                return
                
            # Get trade parameters from command arguments
            if len(args) >= 2:
                asset = args[0].upper()
                direction = args[1].lower()
                amount = float(args[2]) if len(args) >= 3 else 1.0
                
                self.send_message(chat_id, f"Placing {direction} trade on {asset} for ${amount}...")
                success = scraper.place_trade(asset, direction, amount)
                
                if success:
                    logger.info(f"Trade executed successfully: {direction} on {asset} for ${amount}")
                    self.send_message(chat_id, "✅ Trade executed successfully")
                else:
                    logger.error("Failed to execute trade")
                    self.send_message(chat_id, "❌ Failed to execute trade")
            else:
                self.send_message(chat_id, "Please provide asset and direction. Example: /trade EURUSD call 1.0")
                
        except Exception as e:
            logger.error(f"Error executing trade: {str(e)}")
            self.send_message(chat_id, f"Error executing trade: {str(e)}")

    def stop_command(self, chat_id, user_id, args):
        """Handle /stop command."""
        if not self.check_admin(chat_id, user_id):
            return
            
        try:
            if scraper:
                scraper.close()
            logger.info("Trading stopped and connection closed")
            self.send_message(chat_id, "🛑 Trading stopped and connection closed")
        except Exception as e:
            logger.error(f"Error stopping trading: {str(e)}")
            self.send_message(chat_id, f"Error stopping trading: {str(e)}")

    def run(self):
        """Run the bot."""
        logger.info("Bot is running. Press Ctrl+C to stop.")
        
        try:
            while True:
                try:
                    updates = self.get_updates()
                    if updates:
                        self.process_updates(updates)
                except Exception as e:
                    logger.error(f"Error in update loop: {e}")
                    # Continue running even if there's an error
                    
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        finally:
            # Cleanup
            if scraper:
                try:
                    scraper.close()
                except:
                    pass

def main():
    """Start the bot."""
    logger.info("Starting Telegram bot...")
    
    # Create and run the bot
    bot = TelegramBot(TOKEN)
    bot.run()

if __name__ == '__main__':
    main() 