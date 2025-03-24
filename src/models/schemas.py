from typing import List, Optional
from pydantic import BaseModel, Field

class PlayerStats(BaseModel):
    puuid: str = Field(default="")
    champion: str = Field(default="")
    kills: int = Field(default=0)
    deaths: int = Field(default=0)
    assists: int = Field(default=0)
    kda: float = Field(default=0.0)
    cs_total: int = Field(default=0)
    cs_per_min: float = Field(default=0.0)
    vision_score: int = Field(default=0)
    gold_per_min: float = Field(default=0.0)
    damage_per_min: float = Field(default=0.0)
    win: bool = Field(default=False)
    champion_id: int = Field(default=0)
    lane: str = Field(default="UNKNOWN")
    cs_at_10: float = Field(default=0.0)
    gold_diff_at_15: float = Field(default=0.0)
    first_blood: bool = Field(default=False)
    total_damage_to_champions: float = Field(default=0.0)
    total_damage: float = Field(default=0.0)
    total_heal: float = Field(default=0.0)
    total_damage_taken: float = Field(default=0.0)
    dragon_kills: int = Field(default=0)
    baron_kills: int = Field(default=0)
    wards_placed: int = Field(default=0)
    items: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class MatchupStats(BaseModel):
    player: PlayerStats = Field(default_factory=PlayerStats)
    opponent: PlayerStats = Field(default_factory=PlayerStats)

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True