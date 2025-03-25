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

    def get_win_rate(self) -> float:
        if not self.matches:
            return 0.0
        wins = sum(1 for player, _ in self.matches if player.win)
        return wins / len(self.matches)

    def get_average_stats(self) -> Dict:
        if not self.matches:
            return {}

        avg_stats = {
            'kills': 0.0,
            'deaths': 0.0,
            'assists': 0.0,
            'cs_per_min': 0.0,
            'gold_per_min': 0.0,
            'damage_per_min': 0.0,
            'vision_score': 0.0
        }

        for player, _ in self.matches:
            for stat in avg_stats:
                avg_stats[stat] += getattr(player, stat)

        for stat in avg_stats:
            avg_stats[stat] /= len(self.matches)

        return avg_stats

    def get_champion_matchups(self) -> Dict:
        return self._champion_matchups

    def get_advanced_kda(self) -> Dict:
        """Calculate weighted KDA giving more value to kills than assists"""
        if not self.matches:
            return {"weighted_kda": 0.0, "kill_participation": 0.0}

        total_kills = sum(p.kills for p, _ in self.matches)
        total_deaths = sum(p.deaths for p, _ in self.matches)
        total_assists = sum(p.assists for p, _ in self.matches)

        denominator = max(total_deaths, 1)
        weighted_kda = (total_kills * 1.2 + total_assists * 0.8) / denominator

        total_team_kills = sum(p.kills + p.assists for p, _ in self.matches)
        kill_participation = (total_kills + total_assists) / max(total_team_kills, 1)

        return {
            "weighted_kda": weighted_kda,
            "kill_participation": kill_participation
        }

    def get_early_game_analysis(self) -> Dict:
        """Analyze performance in first 15 minutes of games"""
        if not self.matches:
            return {
                "average_cs_at_10": 0.0,
                "first_blood_rate": 0.0,
                "early_gold_diff": 0.0
            }

        return {
            "average_cs_at_10": self._early_game_stats["total_cs"] / len(self.matches),
            "first_blood_rate": self._early_game_stats["first_blood"] / len(self.matches),
            "early_gold_diff": self._early_game_stats["gold_diff"] / len(self.matches)
        }

    def get_damage_analysis(self) -> Dict:
        """Detailed damage statistics"""
        if not self.matches:
            return {
                "dpm": 0.0,
                "total_damage_taken": 0.0,
                "true_heal": 0.0
            }

        total_damage = max(self._damage_analysis["total_damage_taken"], 1)
        return {
            "dpm": self._damage_analysis["total_damage"] / len(self.matches),
            "total_damage_taken": self._damage_analysis["total_damage_taken"] / len(self.matches),
            "total_heal": self._damage_analysis["total_heal"] / total_damage
        }

    def get_objective_analysis(self) -> Dict:
        """Objective control statistics"""
        if not self.matches:
            return {
                "dragon_control": 0.0,
                "baron_control": 0.0,
                "vision_impact": 0.0
            }

        return {
            "dragon_control": self._objective_analysis["dragons"] / len(self.matches),
            "baron_control": self._objective_analysis["barons"] / len(self.matches),
            "vision_impact": self._objective_analysis["wards_placed"] / len(self.matches)
        }

    def get_item_analysis(self) -> Dict:
        """Analyze most effective item builds"""
        if not self.matches:
            return {}

        return {
            champ: {
                "win_rate": data["wins"] / data["count"] if data["count"] > 0 else 0.0,
                "popularity": data["count"] / len(self.matches)
            }
            for champ, data in self._item_builds.items()
        }

    def get_comeback_stats(self) -> Dict:
        """Analyze performance when behind in gold"""
        if not self.matches:
            return {
                "comeback_rate": 0.0,
                "average_comeback_deficit": 0.0
            }

        comeback_games = [(p, o) for p, o in self.matches if p.gold_per_min < o.gold_per_min and p.win]
        comeback_count = len(comeback_games)

        return {
            "comeback_rate": comeback_count / len(self.matches),
            "average_comeback_deficit": sum(
                (o.gold_per_min - p.gold_per_min)
                for (p, o) in comeback_games
            ) / max(comeback_count, 1)
        }

    # Private methods remain the same...

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
        self._damage_analysis["total_damage_to_champions"] += player.total_damage_to_champions
        self._damage_analysis["total_damage"] += player.total_damage
        self._damage_analysis["total_damage_taken"] += player.total_damage_taken

    def _analyze_objectives(self, player: PlayerStats):
        self._objective_analysis["dragons"] += player.dragon_kills
        self._objective_analysis["barons"] += player.baron_kills
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