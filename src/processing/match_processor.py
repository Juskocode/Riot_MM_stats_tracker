from typing import Optional, Dict, Tuple
from ..models.schemas import PlayerStats


class MatchProcessor:
    def __init__(self, strict_validation: bool = True):
        self.strict_validation = strict_validation

    def process_match(self, match_data: Dict, puuid: str) -> Optional[Tuple[PlayerStats, PlayerStats]]:
        try:
            player_data = self._extract_player_data(match_data, puuid)
            print(player_data)
            opponent_data = self._extract_opponent_data(match_data, puuid)
            print(opponent_data)
            if not all([player_data, opponent_data]):
                print("wrong")
                return None

            return (
                PlayerStats(**player_data),
                PlayerStats(**opponent_data)
            )
        except (KeyError, ValueError):
            print("missing key or value error,\n this means extraction of the data is missing some key values of the scheme.")
            return None

    def _extract_player_data(self, match_data: Dict, puuid: str) -> Optional[Dict]:
        participants = match_data['metadata']['participants']
        player_index = participants.index(puuid)
        return self._transform_data(match_data['info']['participants'][player_index])

    def _extract_opponent_data(self, match_data: Dict, puuid: str) -> Optional[Dict]:
        participants = match_data['info']['participants']
        player = next(p for p in participants if p['puuid'] == puuid)

        opponent = next(
            (p for p in participants
             if p['teamId'] != player['teamId']
             and p['teamPosition'] == player['teamPosition']),
            None
        )

        return self._transform_data(opponent) if opponent else None

    def _transform_data(self, participant: Dict) -> Dict:
        time_played = participant.get('timePlayed', 1)
        total_cs = participant.get('totalMinionsKilled', 0) + participant.get('neutralMinionsKilled', 0)

        return {
            'puuid': participant.get('puuid'),
            'champion': participant.get('championName'),
            'kills': participant.get('kills', 0),
            'deaths': participant.get('deaths', 0),
            'assists': participant.get('assists', 0),
            'kda': participant.get('challenges', {}).get('kda', 0),
            'cs_total': total_cs,
            'cs_per_min': total_cs / (time_played / 60) if time_played > 0 else 0,
            'vision_score': participant.get('visionScore', 0),
            'gold_per_min': participant.get('challenges', {}).get('goldPerMinute', 0),
            'damage_per_min': participant.get('challenges', {}).get('damagePerMinute', 0),
            'win': participant.get('win', False),
            'champion_id': participant.get('championId', 0),
            'lane': participant.get('teamPosition', 'N/A'),
            'cs_at_10': participant.get('challenges', {}).get('csAt10', 0),
            'gold_diff_at_15': participant.get('challenges', {}).get('gold_diff_at_15', 0),
            'first_blood' : participant.get('firstBloodKill', False),
            'total_damage_to_champions': participant.get('totalDamageDealtToChampions', 0),
            'total_damage': participant.get('totalDamageDealt', 0),
            'total_heal': participant.get('totalHeal', 0),
            'total_damage_taken': participant.get('totalDamageTaken', 0),
            'dragon_kills': participant.get('dragonKills', 0),
            'baron_kills': participant.get('baronKills', 0),
            'wards_placed': participant.get('wardsPlaced', 0),
            'items': participant.get('items', [])
        }