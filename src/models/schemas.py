from typing import List

from pydantic import BaseModel

class PlayerStats(BaseModel):
    puuid: str
    champion: str
    kills: int
    deaths: int
    assists: int
    kda: float
    cs_total: int
    cs_per_min: float
    vision_score: int
    gold_per_min: float
    damage_per_min: float
    win: bool
    champion_id: int
    lane: str
    cs_at_10: float
    gold_diff_at_15: float
    first_blood: bool
    total_damage: float
    true_damage: float
    damage_share: float
    dragon_kills: int
    rift_herald_kills: int
    wards_placed: int
    items: List[str]
    class Config:
        from_attributes = True

class MatchupStats(BaseModel):
    player: PlayerStats
    opponent: PlayerStats

    class Config:
        from_attributes = True