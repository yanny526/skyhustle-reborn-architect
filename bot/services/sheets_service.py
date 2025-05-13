
"""
Google Sheets service for data storage
"""
import os
import base64
import json
import logging
from typing import Dict, List, Optional, Any

import gspread
from google.oauth2.service_account import Credentials

# Logger
logger = logging.getLogger(__name__)

# Define scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

class Player:
    """Player class representing a row in the players sheet"""
    def __init__(self, user_id: int, data: Dict[str, Any]):
        self.user_id = user_id
        self.commander_name = data.get("commander_name", "")
        self.credits = int(data.get("credits", 0))
        self.fleet_power = int(data.get("fleet_power", 0))
        self.defense_power = int(data.get("defense_power", 0))
        self.last_active = data.get("last_active", "")
    
    def get_power_score(self) -> int:
        """Calculate the total power score of the player"""
        return self.fleet_power + self.defense_power

class SheetsRepository:
    """Repository for interacting with Google Sheets"""
    _client = None
    _spreadsheet = None
    
    @classmethod
    def _initialize(cls):
        """Initialize the Google Sheets client"""
        if cls._client is not None:
            return
        
        try:
            # Get credentials from environment
            credentials_b64 = os.getenv("GOOGLE_CREDENTIALS_B64")
            spreadsheet_id = os.getenv("SPREADSHEET_ID")
            
            if not credentials_b64 or not spreadsheet_id:
                raise ValueError("Missing Google Sheets credentials or spreadsheet ID")
            
            # Decode credentials
            credentials_json = base64.b64decode(credentials_b64).decode('utf-8')
            credentials_info = json.loads(credentials_json)
            
            # Create credentials
            credentials = Credentials.from_service_account_info(
                credentials_info, scopes=SCOPES
            )
            
            # Create client and open spreadsheet
            cls._client = gspread.authorize(credentials)
            cls._spreadsheet = cls._client.open_by_key(spreadsheet_id)
            
            # Initialize required sheets if they don't exist
            cls._ensure_sheets_exist([
                "players", "queues", "battles", "spy_missions", "names"
            ])
            
            logger.info("Google Sheets connection initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Google Sheets: {e}")
            raise
    
    @classmethod
    def _ensure_sheets_exist(cls, sheet_names: List[str]):
        """Ensure that the required sheets exist"""
        existing_sheets = [sheet.title for sheet in cls._spreadsheet.worksheets()]
        
        for sheet_name in sheet_names:
            if sheet_name not in existing_sheets:
                cls._spreadsheet.add_worksheet(
                    title=sheet_name, rows=1000, cols=20
                )
                logger.info(f"Created new sheet: {sheet_name}")
    
    @classmethod
    def get_player(cls, user_id: int) -> Optional[Player]:
        """Get a player by user ID"""
        cls._initialize()
        
        players_sheet = cls._spreadsheet.worksheet("players")
        
        try:
            # Find the player row
            cell = players_sheet.find(str(user_id), in_column=1)
            if cell:
                row = players_sheet.row_values(cell.row)
                headers = players_sheet.row_values(1)
                
                # Create a dictionary from headers and row values
                data = dict(zip(headers, row))
                return Player(user_id, data)
        except Exception as e:
            logger.error(f"Error getting player: {e}")
        
        return None
    
    @classmethod
    def get_leaderboard(cls, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the leaderboard sorted by power score"""
        cls._initialize()
        
        try:
            players_sheet = cls._spreadsheet.worksheet("players")
            all_players = players_sheet.get_all_records()
            
            # Calculate power score and sort
            for player in all_players:
                player["power_score"] = int(player.get("fleet_power", 0)) + int(player.get("defense_power", 0))
                # Ensure user_id is an integer
                player["user_id"] = int(player.get("user_id", 0))
            
            # Sort by power score descending
            sorted_players = sorted(
                all_players, 
                key=lambda p: p["power_score"], 
                reverse=True
            )
            
            # Return limited results
            return sorted_players[:limit]
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
