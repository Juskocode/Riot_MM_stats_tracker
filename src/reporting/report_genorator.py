from pathlib import Path
from typing import List, Tuple
from ..models.schemas import PlayerStats


class ReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_full_report(self, matches: List[Tuple[PlayerStats, PlayerStats]], analyzer: 'StatAnalyzer'):
        sections = [
            self._generate_summary(analyzer),
            self._generate_advanced_kda(analyzer),
            self._generate_early_game(analyzer),
            self._generate_damage(analyzer),
            self._generate_objectives(analyzer),
            self._generate_items(analyzer),
            self._generate_comebacks(analyzer),
            self._generate_details(matches),
            self._generate_matchups(analyzer)
        ]

        content = "\n\n".join(sections)
        self._save_report(content, "full_report.md")

    def _generate_summary(self, analyzer: 'StatAnalyzer') -> str:
        avg_stats = analyzer.get_average_stats()
        return f"""## Overall Summary
- 🏆 Win Rate: {analyzer.get_win_rate() * 100:.1f}%
- ⚔️ Average KDA: {avg_stats.get('kda', 0):.2f}
- 🎯 CS/Min: {avg_stats.get('cs_per_min', 0):.1f}
- 💰 Gold/Min: {avg_stats.get('gold_per_min', 0):.0f}
- 🔥 Damage/Min: {avg_stats.get('damage_per_min', 0):.0f}
"""

    def _generate_advanced_kda(self, analyzer: 'StatAnalyzer') -> str:
        kda_stats = analyzer.get_advanced_kda()
        return f"""## Combat Effectiveness
- ⚖️ Weighted KDA: {kda_stats['weighted_kda']:.2f}
- 🤝 Kill Participation: {kda_stats['kill_participation'] * 100:.1f}%
"""

    def _generate_early_game(self, analyzer: 'StatAnalyzer') -> str:
        early_stats = analyzer.get_early_game_analysis()
        return f"""## Early Game Performance (0-15min)
- 🎯 CS @ 10: {early_stats['average_cs_at_10']:.1f}
- 🩸 First Blood Rate: {early_stats['first_blood_rate'] * 100:.1f}%
- 💰 Gold Diff @ 15: {early_stats['early_gold_diff']:.0f}
"""

    def _generate_damage(self, analyzer: 'StatAnalyzer') -> str:
        damage_stats = analyzer.get_damage_analysis()
        return f"""## Damage Analysis
- 🔥 Damage/Min: {damage_stats['dpm']:.0f}
- 📊 Damage Share: {damage_stats['damage_share'] * 100:.1f}%
- ⚡ True Damage Ratio: {damage_stats['true_damage_ratio'] * 100:.1f}%
"""

    def _generate_objectives(self, analyzer: 'StatAnalyzer') -> str:
        obj_stats = analyzer.get_objective_analysis()
        return f"""## Objective Control
- 🐉 Dragons/Gm: {obj_stats['dragon_control']:.1f}
- 🏰 Heralds/Gm: {obj_stats['herald_control']:.1f}
- 👁️ Wards Placed/Gm: {obj_stats['vision_impact']:.1f}
"""

    def _generate_items(self, analyzer: 'StatAnalyzer') -> str:
        item_stats = analyzer.get_item_analysis()
        lines = [
            "## Item Build Analysis",
            "| Core Items | Win Rate | Popularity |",
            "|------------|----------|------------|"
        ]

        for build, stats in item_stats.items():
            lines.append(
                f"| {build} | {stats['win_rate'] * 100:.1f}% | {stats['popularity'] * 100:.1f}% |"
            )
        return "\n".join(lines)

    def _generate_comebacks(self, analyzer: 'StatAnalyzer') -> str:
        comeback_stats = analyzer.get_comeback_stats()
        return f"""## Comeback Statistics
- ♻️ Comeback Rate: {comeback_stats['comeback_rate'] * 100:.1f}%
- 📉 Avg Deficit: {comeback_stats['average_comeback_deficit']:.0f} Gold/Min
"""

    def _generate_details(self, matches: List[Tuple[PlayerStats, PlayerStats]]) -> str:
        lines = [
            "## Match-by-Match Details",
            "| Match | Champion | K/D/A | CS/min | Gold/min | Dmg/min | Result |",
            "|-------|----------|-------|--------|----------|---------|--------|"
        ]

        for i, (player, _) in enumerate(matches, 1):
            lines.append(
                f"| {i} | {player.champion} | "
                f"{player.kills}/{player.deaths}/{player.assists} | "
                f"{player.cs_per_min:.1f} | {player.gold_per_min:.0f} | "
                f"{player.damage_per_min:.0f} | {'🏆 Win' if player.win else '💀 Loss'} |"
            )
        return "\n".join(lines)

    def _generate_matchups(self, analyzer: 'StatAnalyzer') -> str:
        lines = [
            "## Champion Matchups",
            "| Matchup | Games | Win Rate | KDA Diff | Gold Diff | CS Diff |",
            "|---------|-------|----------|----------|-----------|---------|"
        ]

        for matchup, stats in analyzer.get_champion_matchups().items():
            avg_stats = {
                'kda': stats['kda_diff'] / stats['games'],
                'gold': stats['gold_diff'] / stats['games'],
                'cs': stats['cs_diff'] / stats['games']
            }

            lines.append(
                f"| {matchup} | {stats['games']} | "
                f"{stats['wins'] / stats['games'] * 100:.1f}% | "
                f"{avg_stats['kda']:+.2f} | {avg_stats['gold']:+.1f} | "
                f"{avg_stats['cs']:+.1f} |"
            )
        return "\n".join(lines)

    def _save_report(self, content: str, filename: str):
        path = self.output_dir / filename
        path.write_text(content)
        print(f"✅ Report saved to {path.absolute()}")