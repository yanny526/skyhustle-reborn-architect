
"""
Start command handler for the SkyHustle bot
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler

from bot.utils.ui import create_main_menu

# Logger
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.full_name}) started the bot")
    
    # Welcome message
    welcome_text = (
        f"🚀 *Welcome to SkyHustle, {user.first_name}!* 🚀\n\n"
        "SkyHustle is a space-themed resource management and strategy game.\n\n"
        "To begin your journey as a space commander:\n"
        "1️⃣ Set your commander name with /setname\n"
        "2️⃣ Collect resources in the queue\n"
        "3️⃣ Build your fleet and attack other players\n\n"
        "Ready to dominate the galaxy? Use the menu below!"
    )
    
    # Main menu
    await update.message.reply_text(
        welcome_text,
        reply_markup=create_main_menu(),
        parse_mode="Markdown"
    )

def register_handlers(application):
    """Register start handler with the application"""
    application.add_handler(CommandHandler("start", start))
    
    # Add more basic command handlers here
    # For example: application.add_handler(CommandHandler("help", help_command))
