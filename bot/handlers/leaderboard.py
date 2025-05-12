
"""
Leaderboard system handlers
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
)

from bot.services.sheets_service import SheetsRepository
from bot.utils.ui import (
    create_main_menu,
    section_header,
)

# Logger
logger = logging.getLogger(__name__)

async def handle_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle leaderboard display"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Get player to verify they have a name
    player = SheetsRepository.get_player(user_id)
    
    # Verify player exists and has a name
    if not player or not player.commander_name:
        await query.edit_message_text(
            "❌ You need to set a commander name first with /setname."
        )
        return
    
    # Get leaderboard data
    top_players = SheetsRepository.get_leaderboard(limit=10)
    
    message_text = (
        f"🏆 *SkyHustle Leaderboard* 🏆\n\n"
        f"{section_header('Top Commanders')}\n"
    )
    
    if not top_players:
        message_text += "No players found on the leaderboard yet."
    else:
        # Find player's position
        player_position = None
        for i, p in enumerate(top_players):
            if p["user_id"] == user_id:
                player_position = i + 1
                break
        
        # Display top players
        for i, p in enumerate(top_players):
            # Add trophy emoji for top 3
            position_icon = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
            
            # Highlight the current player
            is_current_player = p["user_id"] == user_id
            name = p["commander_name"]
            
            if is_current_player:
                name = f"👉 {name} 👈"
            
            message_text += f"{position_icon} {name}: {p['power_score']} power\n"
        
        # If player not in top 10, show their position
        if player_position is None:
            message_text += f"\nYour position: Beyond top 10"
        else:
            message_text += f"\nYour position: #{player_position}"
        
        message_text += f"\nYour Power Score: {player.get_power_score()}"
    
    await query.edit_message_text(
        message_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="menu_main")]
        ]),
        parse_mode="Markdown"
    )

def register_handlers(application):
    """Register leaderboard handlers with the application"""
    # Menu handler
    application.add_handler(
        CallbackQueryHandler(handle_leaderboard, pattern="^menu_leaderboard$")
    )
