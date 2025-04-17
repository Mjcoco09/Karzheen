import logging
from telegram import Update
from telegram.ext import ContextTypes
from config.credentials import Credentials

logger = logging.getLogger(__name__)

class CommandHandler:
    def __init__(self):
        self.admin_ids = Credentials.get_admin_ids()

    def is_admin(self, user_id: int) -> bool:
        """Check if user is an admin."""
        return user_id in self.admin_ids

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command."""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("You are not authorized to use this bot.")
            return

        await update.message.reply_text(
            "Welcome to Quotex Trading Bot!\n\n"
            "Available commands:\n"
            "/start - Start the bot\n"
            "/stop - Stop the bot\n"
            "/status - Check bot status\n"
            "/balance - Check account balance\n"
            "/asset [name] - Change trading asset\n"
            "/settings - View/change bot settings\n"
            "/demo - Toggle demo mode\n"
            "/help - Show this help message"
        )

    async def handle_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /stop command."""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("You are not authorized to use this bot.")
            return

        # TODO: Implement stop trading logic
        await update.message.reply_text("Stopping trading operations...")

    async def handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /status command."""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("You are not authorized to use this bot.")
            return

        # TODO: Implement status check logic
        await update.message.reply_text(
            "Bot Status:\n"
            "Trading: Not Active\n"
            "Current Asset: EURUSD\n"
            "Mode: Live\n"
            "Last Trade: None"
        )

    async def handle_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /balance command."""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("You are not authorized to use this bot.")
            return

        # TODO: Implement balance check logic
        await update.message.reply_text("Current Balance: $0.00")

    async def handle_asset(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /asset command."""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("You are not authorized to use this bot.")
            return

        if not context.args:
            await update.message.reply_text("Please specify an asset. Example: /asset EURUSD")
            return

        asset = context.args[0].upper()
        # TODO: Implement asset change logic
        await update.message.reply_text(f"Changing asset to {asset}...")

    async def handle_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /settings command."""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("You are not authorized to use this bot.")
            return

        # TODO: Implement settings display/change logic
        await update.message.reply_text(
            "Current Settings:\n"
            "Risk per trade: 2%\n"
            "Strategy: SMA/RSI\n"
            "Timeframe: 1m\n"
            "Demo Mode: Off"
        )

    async def handle_demo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /demo command."""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("You are not authorized to use this bot.")
            return

        # TODO: Implement demo mode toggle logic
        await update.message.reply_text("Toggling demo mode...")

    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /help command."""
        await self.handle_start(update, context)  # Reuse start command for help 