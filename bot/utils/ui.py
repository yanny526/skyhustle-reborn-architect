
"""
UI utilities for the SkyHustle bot
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def create_main_menu() -> InlineKeyboardMarkup:
    """Create the main menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🎮 Play", callback_data="menu_play"),
            InlineKeyboardButton("🏆 Leaderboard", callback_data="menu_leaderboard")
        ],
        [
            InlineKeyboardButton("📊 Status", callback_data="menu_status"),
            InlineKeyboardButton("ℹ️ Help", callback_data="menu_help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def section_header(title: str) -> str:
    """Create a formatted section header"""
    return f"━━━━ {title} ━━━━"
