import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
from config.credentials import Credentials
from config.config import TELEGRAM_CONFIG

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_ACTION, SELECTING_ASSET, SETTING_PARAMETERS = range(3)

class TelegramBot:
    def __init__(self, trading_bot=None):
        self.token = Credentials.get_telegram_token()
        self.admin_ids = Credentials.get_admin_ids()
        self.application = None
        self.trading_bot = trading_bot

    def set_trading_bot(self, trading_bot):
        """Set the trading bot reference after initialization."""
        self.trading_bot = trading_bot

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the bot and show the main menu."""
        user_id = update.effective_user.id
        if user_id not in self.admin_ids:
            await update.message.reply_text("You are not authorized to use this bot.")
            return ConversationHandler.END

        keyboard = [
            [
                InlineKeyboardButton("Start Trading", callback_data='start_trading'),
                InlineKeyboardButton("Stop Trading", callback_data='stop_trading'),
            ],
            [
                InlineKeyboardButton("Change Asset", callback_data='change_asset'),
                InlineKeyboardButton("Settings", callback_data='settings'),
            ],
            [
                InlineKeyboardButton("Status", callback_data='status'),
                InlineKeyboardButton("Balance", callback_data='balance'),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Welcome to Quotex Trading Bot! Please select an action:",
            reply_markup=reply_markup
        )
        return SELECTING_ACTION

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle button presses."""
        query = update.callback_query
        await query.answer()

        if query.data == 'start_trading':
            if not self.trading_bot.is_trading:
                self.trading_bot.trade_task = asyncio.create_task(self.trading_bot.start_trading())
                await query.edit_message_text("Starting trading...")
            else:
                await query.edit_message_text("Trading is already active")

        elif query.data == 'stop_trading':
            if self.trading_bot.is_trading:
                await self.trading_bot.stop_trading()
                await query.edit_message_text("Stopping trading...")
            else:
                await query.edit_message_text("Trading is not active")

        elif query.data == 'change_asset':
            await query.edit_message_text("Select asset:")
            return SELECTING_ASSET

        elif query.data == 'settings':
            settings = self.trading_bot.strategy.get_strategy_info()
            risk_settings = self.trading_bot.risk_manager.get_risk_settings()
            
            message = (
                "Current Settings:\n\n"
                f"Strategy:\n"
                f"SMA Period: {settings['sma_period']}\n"
                f"RSI Period: {settings['rsi_period']}\n"
                f"RSI Overbought: {settings['rsi_overbought']}\n"
                f"RSI Oversold: {settings['rsi_oversold']}\n\n"
                f"Risk Management:\n"
                f"Risk per Trade: {risk_settings['risk_percentage']*100}%\n"
                f"Min Delay: {risk_settings['min_delay']}s\n"
                f"Max Delay: {risk_settings['max_delay']}s"
            )
            await query.edit_message_text(message)

        elif query.data == 'status':
            stats = self.trading_bot.risk_manager.get_trade_stats()
            message = (
                "Bot Status:\n\n"
                f"Trading: {'Active' if self.trading_bot.is_trading else 'Inactive'}\n"
                f"Current Asset: {self.trading_bot.current_asset}\n"
                f"Mode: {'Demo' if self.trading_bot.quotex.is_demo_mode else 'Live'}\n\n"
                f"Trading Statistics:\n"
                f"Total Trades: {stats['total_trades']}\n"
                f"Win Rate: {stats['win_rate']}%\n"
                f"Profit Factor: {stats['profit_factor']}\n"
                f"Average Win: ${stats['average_win']}\n"
                f"Average Loss: ${stats['average_loss']}"
            )
            await query.edit_message_text(message)

        elif query.data == 'balance':
            balance = self.trading_bot.quotex.get_balance()
            if balance is not None:
                await query.edit_message_text(f"Current Balance: ${balance:.2f}")
            else:
                await query.edit_message_text("Failed to get balance")

        return SELECTING_ACTION

    async def send_trade_notification(self, direction, amount, price, screenshot_path):
        """Send trade notification to all admin users."""
        message = (
            f"New Trade Executed:\n\n"
            f"Direction: {'UP' if direction == 'up' else 'DOWN'}\n"
            f"Amount: ${amount:.2f}\n"
            f"Price: ${price:.2f}"
        )

        for admin_id in self.admin_ids:
            try:
                with open(screenshot_path, 'rb') as photo:
                    await self.application.bot.send_photo(
                        chat_id=admin_id,
                        photo=photo,
                        caption=message
                    )
            except Exception as e:
                logger.error(f"Failed to send trade notification to {admin_id}: {str(e)}")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log errors caused by updates."""
        logger.error(f"Update {update} caused error {context.error}")

    def run(self):
        """Run the bot."""
        self.application = Application.builder().token(self.token).build()

        # Add conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                SELECTING_ACTION: [
                    CallbackQueryHandler(self.button_handler),
                ],
            },
            fallbacks=[CommandHandler('start', self.start)],
        )

        self.application.add_handler(conv_handler)
        self.application.add_error_handler(self.error_handler)

        # Start the bot
        self.application.run_polling(allowed_updates=Update.ALL_TYPES) 