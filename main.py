import logging
import asyncio
import time
from pathlib import Path
from config.config import LOGS_DIR, TRADING_CONFIG
from config.credentials import Credentials
from src.bot.telegram_handler import TelegramBot
from src.bot.command_handler import CommandHandler
from src.scraper.quotex_interface import QuotexInterface
from src.trading.strategy import TradingStrategy
from src.trading.risk_manager import RiskManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        self.telegram_bot = TelegramBot()
        self.command_handler = CommandHandler()
        self.quotex = QuotexInterface(headless=True)
        self.strategy = TradingStrategy()
        self.risk_manager = RiskManager()
        self.is_trading = False
        self.current_asset = TRADING_CONFIG['DEFAULT_ASSET']
        self.trade_task = None
        # Set the trading bot reference in telegram_bot
        self.telegram_bot.set_trading_bot(self)

    async def start_trading(self):
        """Start the trading loop."""
        if self.is_trading:
            logger.warning("Trading is already active")
            return

        self.is_trading = True
        logger.info("Starting trading loop")

        while self.is_trading:
            try:
                # Get current balance
                balance = self.quotex.get_balance()
                if balance is None:
                    logger.error("Failed to get balance")
                    continue

                # Check if we can trade based on risk management
                if not self.risk_manager.can_trade(balance):
                    logger.info("Trading paused due to risk management rules")
                    await asyncio.sleep(60)  # Check again in 1 minute
                    continue

                # Get current price and update strategy
                current_price = self.quotex.get_current_price()
                if current_price is None:
                    logger.error("Failed to get current price")
                    continue

                self.strategy.add_price(current_price)
                signals = self.strategy.calculate_signals()

                if signals and signals['signal']:
                    # Calculate position size
                    position_size = self.risk_manager.calculate_position_size(balance)
                    if position_size is None:
                        continue

                    # Place trade
                    trade_result = self.quotex.place_trade(
                        signals['signal'],
                        position_size
                    )

                    if trade_result:
                        # Take screenshot of the trade
                        screenshot_path = f"screenshots/trade_{int(time.time())}.png"
                        self.quotex.take_screenshot(screenshot_path)

                        # Send trade notification
                        await self.telegram_bot.send_trade_notification(
                            signals['signal'],
                            position_size,
                            current_price,
                            screenshot_path
                        )

                # Wait for next check
                await asyncio.sleep(TRADING_CONFIG['MIN_DELAY'])

            except Exception as e:
                logger.error(f"Error in trading loop: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying

    async def stop_trading(self):
        """Stop the trading loop."""
        self.is_trading = False
        if self.trade_task:
            self.trade_task.cancel()
        logger.info("Trading stopped")

    def start(self):
        """Start the trading bot."""
        try:
            # Initialize Quotex interface
            if not self.quotex.login():
                logger.error("Failed to login to Quotex")
                return

            # Start Telegram bot
            logger.info("Starting Telegram bot...")
            self.telegram_bot.run()

        except Exception as e:
            logger.error(f"Error in main: {str(e)}", exc_info=True)
            raise

    def stop(self):
        """Stop the trading bot."""
        try:
            self.is_trading = False
            self.quotex.close()
            logger.info("Trading bot stopped")
        except Exception as e:
            logger.error(f"Error stopping bot: {str(e)}", exc_info=True)

def main():
    try:
        # Initialize credentials
        telegram_token = Credentials.get_telegram_token()
        quotex_credentials = Credentials.get_quotex_credentials()
        admin_ids = Credentials.get_admin_ids()

        logger.info("Successfully loaded credentials")
        logger.info(f"Admin IDs: {admin_ids}")

        # Initialize and start trading bot
        bot = TradingBot()
        bot.start()

    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 