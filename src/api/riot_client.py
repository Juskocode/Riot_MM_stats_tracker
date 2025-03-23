import requests
from typing import Optional, List, Dict
from config import Settings

class RiotAPIClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update({"X-Riot-Token": self.settings.RIOT_API_KEY})

    def get_puuid(self, game_name: str, tag_line: str) -> Optional[str]:
        url = f"{self.settings.API_BASE_URL}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        try:
            response = self.session.get(url, timeout=self.settings.REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json().get('puuid')
        except (requests.exceptions.RequestException, KeyError):
            return None

    def get_match_ids(self, puuid: str, count: int = 20) -> List[str]:
        url = f"{self.settings.API_BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        try:
            response = self.session.get(
                url,
                params={'count': count},
                timeout=self.settings.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return []

    def get_match_data(self, match_id: str) -> Optional[Dict]:
        url = f"{self.settings.API_BASE_URL}/lol/match/v5/matches/{match_id}"
        try:
            response = self.session.get(url, timeout=self.settings.REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None