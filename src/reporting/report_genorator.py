from pathlib import Path
from typing import List, Tuple
from ..models.schemas import PlayerStats


class ReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_full_report(self, matches: List[Tuple[PlayerStats, PlayerStats]], analyzer: 'StatAnalyzer'):
        summary = self._generate_summary(analyzer)
        details = self._generate_details(matches)
        matchups = self._generate_matchups(analyzer)

        content = f"{summary}\n\n{details}\n\n{matchups}"
        self._save_report(content, "full_report.md")

    def _generate_summary(self, analyzer: 'StatAnalyzer') -> str:
        return f"""## Summary Statistics
- Win Rate: {analyzer.get_win_rate() * 100:.1f}%
- Average KDA: {analyzer.get_average_stats().get('kda', 0):.2f}
- Average CS/min: {analyzer.get_average_stats().get('cs_per_min', 0):.1f}
"""

    def _generate_details(self, matches: List[Tuple[PlayerStats, PlayerStats]]) -> str:
        lines = ["## Match Details", "| Match | Champion | K/D/A | CS/min | Result |"]
        lines.append("|-------|----------|-------|--------|--------|")

        for i, (player, _) in enumerate(matches, 1):
            lines.append(
                f"| {i} | {player.champion} | "
                f"{player.kills}/{player.deaths}/{player.assists} | "
                f"{player.cs_per_min:.1f} | {'Win' if player.win else 'Loss'} |"
            )

        return "\n".join(lines)

    def _generate_matchups(self, analyzer: 'StatAnalyzer') -> str:
        lines = ["## Champion Matchups", "| Matchup | Games | Win Rate |"]
        lines.append("|---------|-------|----------|")

        for matchup, stats in analyzer.get_champion_matchups().items():
            win_rate = stats['wins'] / stats['games'] * 100
            lines.append(f"| {matchup} | {stats['games']} | {win_rate:.1f}% |")

        return "\n".join(lines)

    def _save_report(self, content: str, filename: str):
        path = self.output_dir / filename
        path.write_text(content)