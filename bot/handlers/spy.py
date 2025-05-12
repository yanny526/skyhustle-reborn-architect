
"""
Spy system handlers
"""
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)

from bot.config import CONFIG
from bot.models.player import Player
from bot.models.spy import SpyEngine
from bot.services.sheets_service import SheetsRepository
from bot.utils.ui import (
    create_main_menu,
    create_spy_menu,
    format_time_remaining,
    create_numeric_input_buttons,
    section_header,
)

# Logger
logger = logging.getLogger(__name__)

# Conversation states
SPY_SELECT_TARGET = 1
SPY_SELECT_UNITS = 2
SPY_CONFIRM = 3

# Context data keys
SPY_TARGET = "spy_target"
SPY_DRONES = "spy_drones"

async def handle_spy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle spy menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Get player
    player = SheetsRepository.get_player(user_id)
    
    # Verify player exists and has a name
    if not player or not player.commander_name:
        await query.edit_message_text(
            "❌ You need to set a commander name first with /setname."
        )
        return
    
    # Check if spy center exists
    if player.buildings.spy_center < 1:
        await query.edit_message_text(
            "🛰️ *Spy Center Required* 🛰️\n\n"
            "You need to build a Spy Center to conduct espionage missions.\n\n"
            "Visit the Build menu to construct a Spy Center.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏗️ Go to Build Menu", callback_data="menu_build")],
                [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="menu_main")]
            ])
        )
        return
    
    # Show spy menu
    message_text = (
        f"🛰️ *Espionage Center* 🛰️\n\n"
        f"{section_header('Spy Assets')}\n"
        f"Spy Center: Level {player.buildings.spy_center}\n"
        f"Spy Technology: Level {player.tech.spy_tech}\n"
        f"Spy Drones: {player.units.spy_drones}\n\n"
        
        f"{section_header('Capabilities')}\n"
        "Your spy drones can gather intelligence on enemy bases,\n"
        "including resource levels, building levels, and military units.\n\n"
        "Higher spy tech level increases mission success rate and reduces detection chance.\n\n"
        "Select an option below:"
    )
    
    await query.edit_message_text(
        message_text,
        reply_markup=create_spy_menu(player.buildings.spy_center),
        parse_mode="Markdown"
    )

async def handle_spy_reports(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle spy reports display"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Get player
    player = SheetsRepository.get_player(user_id)
    
    # Verify player exists and has a name
    if not player or not player.commander_name:
        await query.edit_message_text(
            "❌ You need to set a commander name first with /setname."
        )
        return
    
    # Check if spy center exists
    if player.buildings.spy_center < 1:
        await query.edit_message_text(
            "❌ You need to build a Spy Center first.",
            reply_markup=create_main_menu()
        )
        return
    
    # Get spy missions
    missions = SheetsRepository.get_player_spy_missions(user_id, limit=5)
    
    message_text = (
        f"📋 *Spy Reports* 📋\n\n"
        f"{section_header('Recent Missions')}\n"
    )
    
    if not missions:
        message_text += "No spy missions conducted yet. Launch a spy mission to gather intelligence."
    else:
        for i, mission in enumerate(missions):
            # Format timestamp
            mission_time = mission.timestamp.strftime("%Y-%m-%d %H:%M")
            
            message_text += (
                f"{i+1}. {mission_time}\n"
                f"Target: {mission.target_name}\n"
                f"Status: {'✅ Success' if mission.success else '❌ Failed'}\n"
                f"Detected: {'⚠️ Yes' if mission.detected else '🥷 No'}\n"
            )
            
            # If detected and units lost, show losses
            if mission.detected and mission.units_lost:
                units_text = ", ".join(f"{count} {unit}" for unit, count in mission.units_lost.items())
                message_text += f"Lost: {units_text}\n"
            
            # If successful, show some info about what was found
            if mission.success and mission.report:
                message_text += "Intelligence: "
                
                if "resources" in mission.report:
                    message_text += "Resources, "
                if "buildings" in mission.report:
                    message_text += "Buildings, "
                if "units" in mission.report:
                    message_text += "Units, "
                if "tech" in mission.report:
                    message_text += "Technology, "
                
                # Remove trailing comma and space
                message_text = message_text.rstrip(", ") + "\n"
            
            message_text += "\n"
    
    await query.edit_message_text(
        message_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 View Detailed Report", callback_data="spy_report_detail_1")],
            [InlineKeyboardButton("⬅️ Back to Spy Menu", callback_data="menu_spy")]
        ]) if missions else InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back to Spy Menu", callback_data="menu_spy")]
        ]),
        parse_mode="Markdown"
    )

async def handle_report_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle detailed spy report display"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Get the report index from the callback data
    match = re.match(r'spy_report_detail_(\d+)', query.data)
    if not match:
        await query.edit_message_text("❌ Invalid report selection.")
        return
    
    report_idx = int(match.group(1)) - 1
    
    # Get player
    player = SheetsRepository.get_player(user_id)
    
    # Get spy missions
    missions = SheetsRepository.get_player_spy_missions(user_id, limit=5)
    
    if not missions or report_idx >= len(missions):
        await query.edit_message_text(
            "❌ Spy report not found.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back to Spy Menu", callback_data="menu_spy")]
            ])
        )
        return
    
    # Get the specific mission
    mission = missions[report_idx]
    
    message_text = (
        f"🔍 *Detailed Spy Report* 🔍\n\n"
        f"{section_header('Mission Info')}\n"
        f"Target: {mission.target_name}\n"
        f"Time: {mission.timestamp.strftime('%Y-%m-%d %H:%M')}\n"
        f"Status: {'✅ Success' if mission.success else '❌ Failed'}\n"
        f"Detected: {'⚠️ Yes' if mission.detected else '🥷 No'}\n"
    )
    
    # If units lost, show losses
    if mission.units_lost:
        units_text = ", ".join(f"{count} {unit}" for unit, count in mission.units_lost.items())
        message_text += f"Units Lost: {units_text}\n"
    
    # If successful, show detailed report
    if mission.success and mission.report:
        message_text += f"\n{section_header('Intelligence Gathered')}\n"
        
        # Resources
        if "resources" in mission.report:
            message_text += "Resources:\n"
            for resource, amount in mission.report["resources"].items():
                emoji = "⚙️" if resource == "metal" else "💎" if resource == "crystal" else "⛽"
                message_text += f"- {emoji} {resource.capitalize()}: {amount}\n"
        
        # Buildings
        if "buildings" in mission.report:
            message_text += "\nBuildings:\n"
            for building, level in mission.report["buildings"].items():
                building_name = building.replace("_", " ").title()
                message_text += f"- {building_name}: Level {level}\n"
        
        # Units
        if "units" in mission.report:
            message_text += "\nMilitary Units:\n"
            for unit, count in mission.report["units"].items():
                unit_name = unit.replace("_", " ").title()
                message_text += f"- {unit_name}: {count}\n"
        
        # Technology
        if "tech" in mission.report:
            message_text += "\nTechnology:\n"
            for tech, level in mission.report["tech"].items():
                tech_name = tech.replace("_", " ").title()
                message_text += f"- {tech_name}: Level {level}\n"
    else:
        message_text += "\nNo intelligence was gathered from this mission."
    
    # Create navigation buttons
    buttons = []
    
    # Prev/next buttons
    nav_buttons = []
    if report_idx > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data=f"spy_report_detail_{report_idx}"))
    
    if report_idx < len(missions) - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"spy_report_detail_{report_idx + 2}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.append([InlineKeyboardButton("⬅️ Back to Reports", callback_data="spy_reports")])
    
    await query.edit_message_text(
        message_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

async def handle_launch_spy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
    """Handle launching a spy mission"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Get player
    player = SheetsRepository.get_player(user_id)
    
    # Verify player exists and has a name
    if not player or not player.commander_name:
        await query.edit_message_text(
            "❌ You need to set a commander name first with /setname."
        )
        return ConversationHandler.END
    
    # Check if spy center exists
    if player.buildings.spy_center < 1:
        await query.edit_message_text(
            "❌ You need to build a Spy Center first.",
            reply_markup=create_main_menu()
        )
        return ConversationHandler.END
    
    # Check if player has spy drones
    if player.units.spy_drones <= 0:
        await query.edit_message_text(
            "❌ You don't have any spy drones!\n\n"
            "Train some spy drones in the Military menu first.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛠️ Train Units", callback_data="military_train")],
                [InlineKeyboardButton("⬅️ Back", callback_data="menu_spy")]
            ])
        )
        return ConversationHandler.END
    
    # Initialize spy mission context
    context.user_data[SPY_DRONES] = 0
    
    # Show target selection prompt
    message_text = (
        f"🛰️ *Launch Spy Mission* 🛰️\n\n"
        f"{section_header('Spy Assets')}\n"
        f"Spy Drones: {player.units.spy_drones}\n"
        f"Spy Tech: Level {player.tech.spy_tech}\n\n"
        
        f"{section_header('Target Selection')}\n"
        "Enter the commander name of the player you wish to spy on:\n\n"
        "Type /cancel to cancel the mission."
    )
    
    await query.edit_message_text(
        message_text,
        parse_mode="Markdown"
    )
    
    return SPY_SELECT_TARGET

async def handle_spy_target_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
    """Handle target selection for spy mission"""
    user_id = update.effective_user.id
    target_name = update.message.text.strip()
    
    # Get player
    player = SheetsRepository.get_player(user_id)
    
    # Verify player exists and has a name
    if not player or not player.commander_name:
        await update.message.reply_text(
            "❌ You need to set a commander name first with /setname."
        )
        return ConversationHandler.END
    
    # Find target player
    target_player = SheetsRepository.get_player_by_name(target_name)
    
    if not target_player:
        await update.message.reply_text(
            f"❌ Player '{target_name}' not found.\n\n"
            "Please enter a valid commander name or /cancel to cancel."
        )
        return SPY_SELECT_TARGET
    
    # Check if trying to spy on self
    if target_player.user_id == user_id:
        await update.message.reply_text(
            "❌ You cannot spy on yourself!\n\n"
            "Please enter a different commander name or /cancel to cancel."
        )
        return SPY_SELECT_TARGET
    
    # Store target in context
    context.user_data[SPY_TARGET] = target_player
    
    # Show drone count selection
    message_text = (
        f"🛰️ *Spy on {target_player.commander_name}* 🛰️\n\n"
        f"{section_header('Target Info')}\n"
        f"Commander: {target_player.commander_name}\n"
        f"Power Score: {target_player.get_power_score()}\n\n"
        f"Spy Center: Level {target_player.buildings.spy_center if hasattr(target_player.buildings, 'spy_center') else 0}\n\n"
        
        f"{section_header('Spy Mission')}\n"
        f"Available Spy Drones: {player.units.spy_drones}\n\n"
        f"Select how many spy drones to send:"
    )
    
    # Default value (50% of max)
    default_value = max(1, min(player.units.spy_drones, player.units.spy_drones // 2))
    context.user_data[SPY_DRONES] = default_value
    
    # Create markup for selecting drone count
    markup = create_numeric_input_buttons(
        "spy_drones", default_value, 1, player.units.spy_drones, 1, 3, 5
    )
    
    await update.message.reply_text(
        message_text,
        reply_markup=markup,
        parse_mode="Markdown"
    )
    
    return SPY_SELECT_UNITS

async def handle_spy_unit_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
    """Handle spy drone count selection"""
    query = update.callback_query
    await query.answer()
    
    # Parse the callback data
    match1 = re.match(r'spy_drones_(inc|dec)_(\d+)', query.data)
    match2 = re.match(r'spy_drones_confirm_(\d+)', query.data)
    match3 = re.match(r'spy_drones_cancel', query.data)
    
    if match3:
        # Cancel was pressed
        await query.edit_message_text(
            "❌ Spy mission canceled.",
            reply_markup=create_spy_menu(1)  # Assuming spy center exists since we got here
        )
        return ConversationHandler.END
    
    if match1:
        # Increment/decrement button
        action, amount = match1.groups()
        amount = int(amount)
        
        # Current value
        current_count = context.user_data.get(SPY_DRONES, 0)
        
        # Update the count
        if action == "inc":
            # Get player to check max available
            user_id = update.effective_user.id
            player = SheetsRepository.get_player(user_id)
            max_value = player.units.spy_drones
            
            context.user_data[SPY_DRONES] = min(max_value, current_count + amount)
        else:  # dec
            context.user_data[SPY_DRONES] = max(1, current_count - amount)
        
        # Re-render the unit selection
        target_player = context.user_data[SPY_TARGET]
        user_id = update.effective_user.id
        player = SheetsRepository.get_player(user_id)
        
        max_value = player.units.spy_drones
        current_value = context.user_data[SPY_DRONES]
        
        message_text = (
            f"🛰️ *Spy on {target_player.commander_name}* 🛰️\n\n"
            f"{section_header('Target Info')}\n"
            f"Commander: {target_player.commander_name}\n"
            f"Power Score: {target_player.get_power_score()}\n\n"
            f"Spy Center: Level {target_player.buildings.spy_center if hasattr(target_player.buildings, 'spy_center') else 0}\n\n"
            
            f"{section_header('Spy Mission')}\n"
            f"Available Spy Drones: {player.units.spy_drones}\n\n"
            f"Select how many spy drones to send:"
        )
        
        # Create markup for selecting drone count
        markup = create_numeric_input_buttons(
            "spy_drones", current_value, 1, max_value, 1, 3, 5
        )
        
        await query.edit_message_text(
            message_text,
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
        return SPY_SELECT_UNITS
    
    if match2:
        # Confirm button
        count = int(match2.group(1))
        context.user_data[SPY_DRONES] = count
        
        # Show mission confirmation
        await show_spy_confirmation(update, context)
        
        return SPY_CONFIRM
    
    return SPY_SELECT_UNITS

async def show_spy_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show spy mission confirmation screen"""
    query = update.callback_query
    
    # Get selected spy drones
    drone_count = context.user_data.get(SPY_DRONES, 0)
    
    # Get target player
    target_player = context.user_data[SPY_TARGET]
    
    # Prepare confirmation message
    message_text = (
        f"🛰️ *Spy Mission Confirmation* 🛰️\n\n"
        f"{section_header('Target')}\n"
        f"Commander: {target_player.commander_name}\n"
        f"Power Score: {target_player.get_power_score()}\n\n"
        
        f"{section_header('Mission Details')}\n"
        f"Spy Drones: {drone_count}\n\n"
        
        "Higher number of drones increases success chance but also increases risk of detection.\n\n"
        "Are you sure you want to launch this spy mission?"
    )
    
    await query.edit_message_text(
        message_text,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚀 Launch Mission", callback_data="spy_confirm"),
                InlineKeyboardButton("❌ Cancel", callback_data="spy_cancel")
            ]
        ]),
        parse_mode="Markdown"
    )

async def handle_spy_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle spy mission confirmation or cancellation"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "spy_cancel":
        await query.edit_message_text(
            "❌ Spy mission canceled.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back to Spy Menu", callback_data="menu_spy")]
            ])
        )
        return ConversationHandler.END
    
    if query.data == "spy_confirm":
        await process_spy_mission(update, context)
        return ConversationHandler.END
    
    return SPY_CONFIRM

async def process_spy_mission(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process the confirmed spy mission"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Get player and target
    player = SheetsRepository.get_player(user_id)
    target_player = context.user_data[SPY_TARGET]
    
    # Verify player exists
    if not player or not target_player:
        await query.edit_message_text(
            "❌ Player information error. Please try again.",
            reply_markup=create_spy_menu(player.buildings.spy_center)
        )
        return
    
    # Get selected drones
    drone_count = context.user_data.get(SPY_DRONES, 0)
    
    # Verify player has enough drones
    if player.units.spy_drones < drone_count:
        await query.edit_message_text(
            "❌ You don't have enough spy drones.",
            reply_markup=create_spy_menu(player.buildings.spy_center)
        )
        return
    
    # Create target data dict for the spy engine
    target_data = {
        "resources": target_player.resources.dict(),
        "buildings": target_player.buildings.dict(),
        "units": target_player.units.dict(),
        "tech": target_player.tech.dict()
    }
    
    # Resolve spy mission
    spy_mission = SpyEngine.resolve_spy_mission(
        spy_user_id=player.user_id,
        spy_name=player.commander_name,
        target_user_id=target_player.user_id,
        target_name=target_player.commander_name,
        units_sent={"spy_drones": drone_count},
        spy_tech_level=player.tech.spy_tech,
        target_spy_center_level=target_player.buildings.spy_center,
        target_data=target_data
    )
    
    # Apply results: remove spy drones that were lost
    if spy_mission.units_lost and "spy_drones" in spy_mission.units_lost:
        lost_drones = spy_mission.units_lost["spy_drones"]
        player.units.spy_drones -= lost_drones
    
    # Save player
    SheetsRepository.save_player(player)
    
    # Save spy mission
    SheetsRepository.save_spy_mission(spy_mission)
    
    # Prepare mission report
    message_text = (
        f"🛰️ *Spy Mission Report* 🛰️\n\n"
        f"{section_header('Mission Status')}\n"
        f"Target: {target_player.commander_name}\n"
        f"Success: {'✅ Yes' if spy_mission.success else '❌ No'}\n"
        f"Detected: {'⚠️ Yes' if spy_mission.detected else '🥷 No'}\n"
    )
    
    # Report on losses if any
    if spy_mission.units_lost:
        drones_lost = spy_mission.units_lost.get("spy_drones", 0)
        if drones_lost > 0:
            message_text += f"Drones Lost: {drones_lost}\n"
    
    # Add intelligence gathered if successful
    if spy_mission.success and spy_mission.report:
        message_text += f"\n{section_header('Intelligence Gathered')}\n"
        
        # Resources
        if "resources" in spy_mission.report:
            message_text += "Resources:\n"
            for resource, amount in spy_mission.report["resources"].items():
                emoji = "⚙️" if resource == "metal" else "💎" if resource == "crystal" else "⛽"
                message_text += f"- {emoji} {resource.capitalize()}: {amount}\n"
        
        # Buildings (show only a few key ones for brevity)
        if "buildings" in spy_mission.report:
            message_text += "\nKey Buildings:\n"
            key_buildings = ["command_center", "barracks", "shipyard", "defense_platform"]
            for building in key_buildings:
                if building in spy_mission.report["buildings"]:
                    building_name = building.replace("_", " ").title()
                    message_text += f"- {building_name}: Level {spy_mission.report['buildings'][building]}\n"
        
        # Units (show only military units for brevity)
        if "units" in spy_mission.report:
            message_text += "\nMilitary Units:\n"
            military_units = ["fighters", "bombers", "cruisers"]
            for unit in military_units:
                if unit in spy_mission.report["units"]:
                    unit_name = unit.replace("_", " ").title()
                    message_text += f"- {unit_name}: {spy_mission.report['units'][unit]}\n"
        
        # Add a teaser if there's more info available
        message_text += "\nView detailed report in the Spy Reports section."
    elif not spy_mission.success:
        message_text += "\nThe mission failed to gather any intelligence."
    
    await query.edit_message_text(
        message_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back to Spy Menu", callback_data="menu_spy")],
            [InlineKeyboardButton("📋 View All Reports", callback_data="spy_reports")]
        ]),
        parse_mode="Markdown"
    )
    
    # Send notification to target if they were detected
    if spy_mission.detected:
        try:
            await context.bot.send_message(
                chat_id=target_player.user_id,
                text=f"⚠️ *SPY ALERT!* ⚠️\n\nYour security systems have detected spy drones from {player.commander_name}!",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to notify target of spy detection: {e}")

async def cancel_spy_mission(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the spy mission process"""
    await update.message.reply_text(
        "❌ Spy mission canceled.",
        reply_markup=create_spy_menu(1)  # Assuming spy center exists since we got here
    )
    return ConversationHandler.END

def register_handlers(application):
    """Register spy system handlers with the application"""
    # Spy menu handler
    application.add_handler(
        CallbackQueryHandler(handle_spy_menu, pattern="^menu_spy$")
    )
    
    # Spy reports handler
    application.add_handler(
        CallbackQueryHandler(handle_spy_reports, pattern="^spy_reports$")
    )
    
    # Detailed spy report handler
    application.add_handler(
        CallbackQueryHandler(handle_report_detail, pattern="^spy_report_detail_\d+$")
    )
    
    # Launch spy mission conversation handler
    spy_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handle_launch_spy, pattern="^spy_launch$")
        ],
        states={
            SPY_SELECT_TARGET: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_spy_target_selection)
            ],
            SPY_SELECT_UNITS: [
                CallbackQueryHandler(handle_spy_unit_selection, pattern="^spy_drones_")
            ],
            SPY_CONFIRM: [
                CallbackQueryHandler(handle_spy_confirmation, pattern="^spy_")
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_spy_mission),
            CallbackQueryHandler(cancel_spy_mission, pattern="^menu_")
        ]
    )
    
    application.add_handler(spy_conv_handler)
