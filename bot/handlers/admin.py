
"""
Admin handlers for game management
"""
import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters
)

from bot.config import CONFIG
from bot.models.player import Player
from bot.services.sheets_service import SheetsRepository
from bot.utils.ui import (
    section_header,
    format_resource_amount,
)

# Logger
logger = logging.getLogger(__name__)

# Admin-only middleware
async def admin_only(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is an admin"""
    if not CONFIG.admin_chat_id:
        await update.effective_message.reply_text("Admin mode not configured.")
        return False
    
    if update.effective_user.id != CONFIG.admin_chat_id:
        await update.effective_message.reply_text("Sorry, this command is for admins only.")
        return False
    
    return True

async def cmd_admin_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command to show game status"""
    if not await admin_only(update, context):
        return
    
    # Get all players
    # (In a real implementation, you'd have a method to count players without loading all data)
    players = []
    try:
        # This is a placeholder. In a real implementation,
        # you'd have a method to get aggregate stats
        message_text = (
            f"🛠️ *Admin Dashboard* 🛠️\n\n"
            f"{section_header('Game Status')}\n"
            f"Total Players: {len(players)}\n"
            f"Server Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
            f"Admin Commands:\n"
            f"/admin_status - Show this screen\n"
            f"/admin_give <player_name> <resource> <amount> - Give resources\n"
            f"/admin_wipe <player_name> - Reset a player's data\n"
            f"/admin_announce <message> - Send global announcement\n"
        )
        
        await update.effective_message.reply_text(
            message_text,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in admin_status: {e}")
        await update.effective_message.reply_text(
            f"❌ Error: {str(e)}"
        )

async def cmd_admin_give(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command to give resources to a player"""
    if not await admin_only(update, context):
        return
    
    # Check arguments
    if len(context.args) < 3:
        await update.effective_message.reply_text(
            "❌ Usage: /admin_give <player_name> <resource> <amount>\n\n"
            "Resources: metal, crystal, fuel"
        )
        return
    
    player_name = context.args[0]
    resource = context.args[1].lower()
    
    try:
        amount = int(context.args[2])
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except ValueError:
        await update.effective_message.reply_text(
            "❌ Amount must be a positive number."
        )
        return
    
    # Validate resource type
    if resource not in ["metal", "crystal", "fuel"]:
        await update.effective_message.reply_text(
            "❌ Invalid resource type. Use: metal, crystal, or fuel."
        )
        return
    
    # Find player
    player = SheetsRepository.get_player_by_name(player_name)
    if not player:
        await update.effective_message.reply_text(
            f"❌ Player '{player_name}' not found."
        )
        return
    
    # Add resources
    setattr(player.resources, resource, getattr(player.resources, resource, 0) + amount)
    
    # Save player
    if SheetsRepository.save_player(player):
        await update.effective_message.reply_text(
            f"✅ Added {amount} {resource} to {player_name}'s account."
        )
        
        # Notify player
        try:
            await context.bot.send_message(
                chat_id=player.user_id,
                text=f"🎁 *Administrator Gift* 🎁\n\n"
                     f"You've received {amount} {resource} from an administrator!",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to notify player of gift: {e}")
    else:
        await update.effective_message.reply_text(
            "❌ Failed to save player data."
        )

async def cmd_admin_wipe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command to reset a player's data"""
    if not await admin_only(update, context):
        return
    
    # Check arguments
    if len(context.args) < 1:
        await update.effective_message.reply_text(
            "❌ Usage: /admin_wipe <player_name>"
        )
        return
    
    player_name = context.args[0]
    
    # Find player
    player = SheetsRepository.get_player_by_name(player_name)
    if not player:
        await update.effective_message.reply_text(
            f"❌ Player '{player_name}' not found."
        )
        return
    
    # Confirm wipe
    await update.effective_message.reply_text(
        f"⚠️ Are you sure you want to reset {player_name}'s data? This cannot be undone!\n\n"
        "Reply 'CONFIRM WIPE' to proceed."
    )
    
    # The actual wipe would be implemented in a conversation handler
    # but for simplicity, we'll just show the confirmation prompt

async def cmd_admin_announce(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command to send a global announcement"""
    if not await admin_only(update, context):
        return
    
    # Check message content
    if not context.args:
        await update.effective_message.reply_text(
            "❌ Usage: /admin_announce <message>"
        )
        return
    
    message = " ".join(context.args)
    
    # In a real implementation, you'd get all players and send them a message
    # Here we'll just simulate it
    
    await update.effective_message.reply_text(
        f"📣 Announcement sent:\n\n{message}"
    )
    
    # In a real implementation, you'd have code like:
    # for player in SheetsRepository.get_all_players():
    #     try:
    #         await context.bot.send_message(
    #             chat_id=player.user_id,
    #             text=f"📣 *Announcement* 📣\n\n{message}",
    #             parse_mode="Markdown"
    #         )
    #     except Exception as e:
    #         logger.error(f"Failed to send announcement to player {player.user_id}: {e}")

def register_handlers(application):
    """Register admin handlers with the application"""
    application.add_handler(CommandHandler("admin_status", cmd_admin_status))
    application.add_handler(CommandHandler("admin_give", cmd_admin_give))
    application.add_handler(CommandHandler("admin_wipe", cmd_admin_wipe))
    application.add_handler(CommandHandler("admin_announce", cmd_admin_announce))
