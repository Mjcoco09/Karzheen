#!/usr/bin/env python3
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
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

def check_admin(update: Update):
    """Check if the user is an admin."""
    user_id = update.effective_user.id
    is_admin = user_id in ADMIN_USER_IDS
    logger.info(f"Admin check for user {user_id}: {is_admin}")
    return is_admin

def start(update: Update, context: CallbackContext):
    """Start the bot and connect to Quotex."""
    global scraper

    logger.info(f"Start command received from user {update.effective_user.id}")
    
    if not check_admin(update):
        update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    try:
        update.message.reply_text("Connecting to Quotex... This may take a moment.")
        
        # Initialize and setup the scraper
        scraper = QuotexScraper()
        scraper.setup_driver()
        
        # Login to Quotex
        if scraper.login():
            logger.info("Successfully connected to Quotex")
            update.message.reply_text('✅ Bot is connected to Quotex! Use /help to see available commands.')
        else:
            logger.error("Failed to connect to Quotex")
            update.message.reply_text('❌ Failed to connect to Quotex. Please check the logs and try again later.')
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")
        update.message.reply_text(f'❌ Error: {str(e)}')

def help_command(update: Update, context: CallbackContext):
    """Send help message with available commands."""
    logger.info(f"Help command received from user {update.effective_user.id}")
    
    if not check_admin(update):
        update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return
        
    help_text = """
Available commands:
/start - Connect to Quotex
/help - Show this help message
/status - Check trading status
/balance - Check account balance
/trade - Execute a trade
/stop - Stop and close connection
    """
    update.message.reply_text(help_text)

def status(update: Update, context: CallbackContext):
    """Check trading status."""
    logger.info(f"Status command received from user {update.effective_user.id}")
    
    if not check_admin(update):
        update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return
    
    try:
        if scraper and scraper.driver:
            status_text = "✅ Bot is connected and running"
        else:
            status_text = "❌ Bot is not connected. Use /start to reconnect."
        
        logger.info(f"Status: {status_text}")
        update.message.reply_text(status_text)
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")
        update.message.reply_text(f"Error checking status: {str(e)}")

def balance(update: Update, context: CallbackContext):
    """Check account balance."""
    logger.info(f"Balance command received from user {update.effective_user.id}")
    
    if not check_admin(update):
        update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return
    
    try:
        if not scraper or not scraper.driver:
            update.message.reply_text("❌ Not connected to Quotex. Use /start to reconnect.")
            return
            
        balance = scraper.get_balance()
        if balance:
            logger.info(f"Balance retrieved: {balance}")
            update.message.reply_text(f"💰 Current balance: ${balance}")
        else:
            logger.error("Failed to get balance")
            update.message.reply_text("❌ Failed to get balance")
    except Exception as e:
        logger.error(f"Error checking balance: {str(e)}")
        update.message.reply_text(f"Error checking balance: {str(e)}")

def trade(update: Update, context: CallbackContext):
    """Execute a trade."""
    logger.info(f"Trade command received from user {update.effective_user.id}")
    
    if not check_admin(update):
        update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return
    
    try:
        if not scraper or not scraper.driver:
            update.message.reply_text("❌ Not connected to Quotex. Use /start to reconnect.")
            return
            
        # Get trade parameters from command arguments
        args = context.args
        if len(args) >= 2:
            asset = args[0].upper()
            direction = args[1].lower()
            amount = float(args[2]) if len(args) >= 3 else 1.0
            
            update.message.reply_text(f"Placing {direction} trade on {asset} for ${amount}...")
            success = scraper.place_trade(asset, direction, amount)
            
            if success:
                logger.info(f"Trade executed successfully: {direction} on {asset} for ${amount}")
                update.message.reply_text("✅ Trade executed successfully")
            else:
                logger.error("Failed to execute trade")
                update.message.reply_text("❌ Failed to execute trade")
        else:
            update.message.reply_text("Please provide asset and direction. Example: /trade EURUSD call 1.0")
            
    except Exception as e:
        logger.error(f"Error executing trade: {str(e)}")
        update.message.reply_text(f"Error executing trade: {str(e)}")

def stop(update: Update, context: CallbackContext):
    """Stop all trading."""
    logger.info(f"Stop command received from user {update.effective_user.id}")
    
    if not check_admin(update):
        update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return
    
    try:
        if scraper:
            scraper.close()
        logger.info("Trading stopped and connection closed")
        update.message.reply_text("🛑 Trading stopped and connection closed")
    except Exception as e:
        logger.error(f"Error stopping trading: {str(e)}")
        update.message.reply_text(f"Error stopping trading: {str(e)}")

def main():
    """Start the bot."""
    logger.info("Starting Telegram bot...")
    
    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("status", status))
    dispatcher.add_handler(CommandHandler("balance", balance))
    dispatcher.add_handler(CommandHandler("trade", trade))
    dispatcher.add_handler(CommandHandler("stop", stop))

    # Start the Bot
    logger.info("Bot is running. Press Ctrl+C to stop.")
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main() 