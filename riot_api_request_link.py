import requests
import os
from typing import List, Dict, Tuple, Optional
from requests.exceptions import HTTPError
from dotenv import load_dotenv

load_dotenv()


class RiotAPIClient:
    BASE_URL = "https://europe.api.riotgames.com"

    def __init__(self):
        self.api_key = os.getenv('RIOT_API_KEY')
        self.session = requests.Session()
        self.session.headers.update({"X-Riot-Token": self.api_key})

    def _handle_response(self, response: requests.Response):
        try:
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return None

    def get_puuid(self, game_name: str, tagline: str) -> Optional[str]:
        url = f"{self.BASE_URL}/riot/account/v1/accounts/by-riot-id/{game_name}/{tagline}"
        response = self.session.get(url)
        data = self._handle_response(response)
        return data.get('puuid') if data else None

    def get_match_ids(self, puuid: str, start: int = 0, count: int = 20) -> List[str]:
        url = f"{self.BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {'start': start, 'count': count}
        response = self.session.get(url, params=params)
        return self._handle_response(response) or []

    def get_match_data(self, match_id: str) -> Optional[dict]:
        url = f"{self.BASE_URL}/lol/match/v5/matches/{match_id}"
        response = self.session.get(url)
        return self._handle_response(response)


class MatchProcessor:
    @staticmethod
    def get_player_stats(match_data: dict, puuid: str) -> Optional[dict]:
        try:
            participants = match_data['metadata']['participants']
            player_index = participants.index(puuid)
            player_data = match_data['info']['participants'][player_index]
            return MatchProcessor._extract_stats(player_data)
        except (ValueError, KeyError):
            return None

    @staticmethod
    def get_opponent_stats(match_data: dict, puuid: str) -> Optional[dict]:
        try:
            participants = match_data['info']['participants']
            player = next(p for p in participants if p['puuid'] == puuid)
            lane = player['teamPosition']
            opponent = next(
                (p for p in participants
                 if p['teamId'] != player['teamId'] and p['teamPosition'] == lane),
                None
            )
            return MatchProcessor._extract_stats(opponent) if opponent else None
        except (StopIteration, KeyError):
            return None

    @staticmethod
    def _extract_stats(player_data: dict) -> dict:
        if not player_data:
            return {}

        time_played = player_data.get('timePlayed', 1)
        total_cs = player_data.get('totalMinionsKilled', 0) + player_data.get('neutralMinionsKilled', 0)

        return {
            'champion': player_data.get('championName', 'Unknown'),
            'lane': player_data.get('teamPosition', 'N/A'),
            'kills': player_data.get('kills', 0),
            'deaths': player_data.get('deaths', 0),
            'assists': player_data.get('assists', 0),
            'kda': player_data.get('challenges', {}).get('kda', 0),
            'cs_total': total_cs,
            'cs_per_min': total_cs / (time_played / 60) if time_played > 0 else 0,
            'vision_score': player_data.get('visionScore', 0),
            'gold_per_min': player_data.get('challenges', {}).get('goldPerMinute', 0),
            'damage_per_min': player_data.get('challenges', {}).get('damagePerMinute', 0),
            'win': player_data.get('win', False),
            'champion_id': player_data.get('championId', 0)
        }


class StatAnalyzer:
    def __init__(self):
        self.matches: List[Tuple[dict, dict]] = []

    def add_match(self, player_stats: dict, opponent_stats: dict):
        if player_stats and opponent_stats:
            self.matches.append((player_stats, opponent_stats))

    def get_average_stats(self) -> dict:
        player_totals = {}
        opponent_totals = {}

        for player, opponent in self.matches:
            for key in player:
                if isinstance(player[key], (int, float)):
                    player_totals[key] = player_totals.get(key, 0) + player[key]
                    opponent_totals[key] = opponent_totals.get(key, 0) + opponent[key]

        avg_stats = {}
        for key in player_totals:
            count = len(self.matches)
            avg_stats[f'player_{key}'] = player_totals[key] / count
            avg_stats[f'opponent_{key}'] = opponent_totals[key] / count

        return avg_stats

    def get_win_rate(self) -> float:
        wins = sum(1 for player, _ in self.matches if player.get('win', False))
        return wins / len(self.matches) if self.matches else 0

    def get_champion_matchups(self) -> Dict[str, Dict]:
        matchups = {}
        for player, opponent in self.matches:
            champ = opponent['champion']
            if champ not in matchups:
                matchups[champ] = {
                    'games': 0,
                    'wins': 0,
                    'avg_kda_diff': 0
                }
            matchups[champ]['games'] += 1
            matchups[champ]['wins'] += 1 if player['win'] else 0
            matchups[champ]['avg_kda_diff'] += (player['kda'] - opponent['kda'])

        for champ in matchups:
            matchups[champ]['avg_kda_diff'] /= matchups[champ]['games']
            matchups[champ]['win_rate'] = matchups[champ]['wins'] / matchups[champ]['games']

        return matchups


class ReportGenerator:
    @staticmethod
    def generate_summary_report(analyzer: StatAnalyzer) -> str:
        content = ["# Player Performance Summary\n"]

        # Win Rate
        content.append(f"## Overall Win Rate\n{analyzer.get_win_rate() * 100:.1f}%\n")

        # Average Stats Comparison
        avg_stats = analyzer.get_average_stats()
        content.append("## Average Stats Comparison\n")
        content.append("| Stat | Player | Opponent | Difference |")
        content.append("|------|--------|----------|------------|")

        comparable_stats = ['kills', 'deaths', 'assists', 'cs_per_min',
                            'gold_per_min', 'damage_per_min', 'vision_score']
        for stat in comparable_stats:
            player = avg_stats.get(f'player_{stat}', 0)
            opponent = avg_stats.get(f'opponent_{stat}', 0)
            diff = player - opponent
            content.append(f"| {stat.replace('_', ' ').title()} | {player:.1f} | {opponent:.1f} | {diff:+.1f} |")

        # Champion Matchups
        content.append("\n## Champion Matchups\n")
        content.append("| Champion | Games | Win Rate | Avg KDA Diff |")
        content.append("|----------|-------|----------|--------------|")
        for champ, stats in analyzer.get_champion_matchups().items():
            content.append(
                f"| {champ} | {stats['games']} | {stats['win_rate'] * 100:.1f}% | {stats['avg_kda_diff']:+.2f} |"
            )

        return '\n'.join(content)

    @staticmethod
    def generate_detailed_report(matches: List[Tuple[dict, dict]]) -> str:
        content = ["# Detailed Match-by-Match Comparison\n"]
        content.append("| Match | Champion (You) | Champion (Opp) | K/D/A | CS/min | Gold/min | Dmg/min | Result |")
        content.append("|-------|----------------|----------------|-------|--------|----------|---------|--------|")

        for i, (player, opponent) in enumerate(matches, 1):
            content.append(
                f"| {i} | {player['champion']} | {opponent['champion']} | "
                f"{player['kills']}/{player['deaths']}/{player['assists']} | "
                f"{player['cs_per_min']:.1f} | {player['gold_per_min']:.0f} | "
                f"{player['damage_per_min']:.0f} | {'Win' if player['win'] else 'Loss'} |"
            )

        return '\n'.join(content)

    @staticmethod
    def save_report(content: str, filename: str):
        try:
            with open(filename, 'w') as f:
                f.write(content)
            print(f"Report saved to {filename}")
        except Exception as e:
            print(f"Error saving report: {e}")


def main():
    # Initialize components
    api_client = RiotAPIClient()
    analyzer = StatAnalyzer()

    # Fetch player data
    puuid = api_client.get_puuid("Autumn", "Zico")
    if not puuid:
        print("Failed to fetch PUUID")
        return

    # Get match history
    match_ids = api_client.get_match_ids(puuid, count=10)

    # Process matches
    for match_id in match_ids:
        match_data = api_client.get_match_data(match_id)
        if match_data:
            player_stats = MatchProcessor.get_player_stats(match_data, puuid)
            opponent_stats = MatchProcessor.get_opponent_stats(match_data, puuid)
            if player_stats and opponent_stats:
                analyzer.add_match(player_stats, opponent_stats)

    # Generate reports
    summary_report = ReportGenerator.generate_summary_report(analyzer)
    detailed_report = ReportGenerator.generate_detailed_report(analyzer.matches)

    full_report = f"{summary_report}\n\n{detailed_report}"
    ReportGenerator.save_report(full_report, "performance_report.md")


if __name__ == "__main__":
    main()