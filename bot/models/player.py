
"""
Player model for SkyHustle game
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone

@dataclass
class Resources:
    """Player resources"""
    metal: int = 100
    crystal: int = 50
    fuel: int = 25

@dataclass
class Fleet:
    """Player fleet"""
    fighters: int = 0
    cruisers: int = 0
    battleships: int = 0

@dataclass
class Player:
    """Player data model"""
    user_id: int
    commander_name: Optional[str] = None
    resources: Resources = field(default_factory=Resources)
    fleet: Fleet = field(default_factory=Fleet)
    last_resource_claim: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    experience: int = 0
    
    def get_power_score(self) -> int:
        """Calculate player's power score"""
        fleet_power = (self.fleet.fighters * 10) + \
                     (self.fleet.cruisers * 50) + \
                     (self.fleet.battleships * 250)
        return fleet_power + (self.experience // 10)
