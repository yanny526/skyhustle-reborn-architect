
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

def format_resource_amount(amount: int) -> str:
    """Format resource amounts with K, M, B suffixes"""
    if amount < 1000:
        return str(amount)
    elif amount < 1000000:
        return f"{amount/1000:.1f}K"
    elif amount < 1000000000:
        return f"{amount/1000000:.1f}M"
    else:
        return f"{amount/1000000000:.1f}B"
