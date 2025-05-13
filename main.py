
#!/usr/bin/env python
"""
SkyHustle Telegram Bot - Main Entry Point
"""
import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main() -> None:
    """Start the bot."""
    # Get the token from the environment variables
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("No TELEGRAM_TOKEN found in environment variables!")

    # Create the Application
    application = Application.builder().token(token).build()

    # Import handlers (importing here to avoid circular imports)
    from bot.handlers.start import register_handlers as register_start_handlers
    from bot.handlers.admin import register_handlers as register_admin_handlers
    from bot.handlers.leaderboard import register_handlers as register_leaderboard_handlers
    from bot.handlers.spy import register_handlers as register_spy_handlers
    
    # Register all handlers
    register_start_handlers(application)
    register_admin_handlers(application)
    register_leaderboard_handlers(application)
    register_spy_handlers(application)
    
    # Start the Bot until you press Ctrl-C
    logger.info("Starting SkyHustle bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
