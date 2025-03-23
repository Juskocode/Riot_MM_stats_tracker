from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from ..models.schemas import PlayerStats


class StatAnalyzer:
    def __init__(self):
        self.matches: List[Tuple[PlayerStats, PlayerStats]] = []
        self._champion_matchups: Dict[str, Dict] = {}
        self._item_builds: Dict[str, Dict] = defaultdict(lambda: {"count": 0, "wins": 0})
        self._early_game_stats: Dict[str, float] = defaultdict(float)
        self._damage_analysis: Dict[str, float] = defaultdict(float)
        self._objective_analysis: Dict[str, float] = defaultdict(float)

    def add_match(self, player_stats: PlayerStats, opponent_stats: PlayerStats):
        self.matches.append((player_stats, opponent_stats))
        self._update_champion_matchups(player_stats, opponent_stats)
        self._track_item_builds(player_stats)
        self._analyze_early_game(player_stats)
        self._analyze_damage_patterns(player_stats)
        self._analyze_objectives(player_stats)

    # Existing methods remain here...

    def get_advanced_kda(self) -> Dict:
        """Calculate weighted KDA giving more value to kills than assists"""
        total_kills = sum(p.kills for p, _ in self.matches)
        total_deaths = sum(p.deaths for p, _ in self.matches)
        total_assists = sum(p.assists for p, _ in self.matches)

        weighted_kda = (total_kills * 1.2 + total_assists * 0.8) / max(total_deaths, 1)
        return {
            "weighted_kda": weighted_kda,
            "kill_participation": (total_kills + total_assists) /
                                  max(sum(p.kills + p.assists for p, _ in self.matches), 1)
        }

    def get_early_game_analysis(self) -> Dict:
        """Analyze performance in first 15 minutes of games"""
        return {
            "average_cs_at_10": self._early_game_stats["total_cs"] / len(self.matches),
            "first_blood_rate": self._early_game_stats["first_blood"] / len(self.matches),
            "early_gold_diff": self._early_game_stats["gold_diff"] / len(self.matches)
        }

    def get_damage_analysis(self) -> Dict:
        """Detailed damage statistics"""
        return {
            "dpm": self._damage_analysis["total_damage"] / len(self.matches),
            "damage_share": self._damage_analysis["damage_share"] / len(self.matches),
            "true_damage_ratio": self._damage_analysis["true_damage"] /
                                 max(self._damage_analysis["total_damage"], 1)
        }

    def get_objective_analysis(self) -> Dict:
        """Objective control statistics"""
        return {
            "dragon_control": self._objective_analysis["dragons"] / len(self.matches),
            "herald_control": self._objective_analysis["heralds"] / len(self.matches),
            "vision_impact": self._objective_analysis["wards_placed"] / len(self.matches)
        }

    def get_item_analysis(self) -> Dict:
        """Analyze most effective item builds"""
        return {
            champ: {
                "win_rate": data["wins"] / data["count"],
                "popularity": data["count"] / len(self.matches)
            }
            for champ, data in self._item_builds.items()
        }

    def get_comeback_stats(self) -> Dict:
        """Analyze performance when behind in gold"""
        comeback_games = [p for p, _ in self.matches if p.gold_per_min < p.opponent.gold_per_min and p.win]
        return {
            "comeback_rate": len(comeback_games) / len(self.matches),
            "average_comeback_deficit": sum(
                (p.opponent.gold_per_min - p.gold_per_min)
                for p in comeback_games
            ) / max(len(comeback_games), 1)
        }

    # Private analysis methods
    def _track_item_builds(self, player: PlayerStats):
        # Simplified example - track first 3 core items
        core_items = sorted(player.items)[:3]  # Assuming items field exists in PlayerStats
        build_key = "-".join(core_items)
        self._item_builds[build_key]["count"] += 1
        if player.win:
            self._item_builds[build_key]["wins"] += 1

    def _analyze_early_game(self, player: PlayerStats):
        # Assuming these fields exist in PlayerStats
        self._early_game_stats["total_cs"] += player.cs_at_10
        self._early_game_stats["gold_diff"] += player.gold_diff_at_15
        if player.first_blood:
            self._early_game_stats["first_blood"] += 1

    def _analyze_damage_patterns(self, player: PlayerStats):
        self._damage_analysis["total_damage"] += player.total_damage
        self._damage_analysis["true_damage"] += player.true_damage
        self._damage_analysis["damage_share"] += player.damage_share

    def _analyze_objectives(self, player: PlayerStats):
        self._objective_analysis["dragons"] += player.dragon_kills
        self._objective_analysis["heralds"] += player.rift_herald_kills
        self._objective_analysis["wards_placed"] += player.wards_placed

    # Enhanced matchup analysis
    def _update_champion_matchups(self, player: PlayerStats, opponent: PlayerStats):
        key = f"{player.champion}_vs_{opponent.champion}"

        if key not in self._champion_matchups:
            self._champion_matchups[key] = {
                "games": 0,
                "wins": 0,
                "kda_diff": 0.0,
                "gold_diff": 0.0,
                "cs_diff": 0.0,
                "damage_diff": 0.0
            }

        matchup = self._champion_matchups[key]
        matchup["games"] += 1
        matchup["wins"] += 1 if player.win else 0
        matchup["kda_diff"] += (player.kda - opponent.kda)
        matchup["gold_diff"] += (player.gold_per_min - opponent.gold_per_min)
        matchup["cs_diff"] += (player.cs_per_min - opponent.cs_per_min)
        matchup["damage_diff"] += (player.damage_per_min - opponent.damage_per_min)