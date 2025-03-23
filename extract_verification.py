import requests
import os
from requests.exceptions import HTTPError

# Configuration
RIOT_API_KEY = 'RGAPI-1b6f4661-b981-4133-946f-19ecc263f280'
SUMMONER_NAME = "Autumn"
TAG_LINE = "Zico"
REGION = "europe"
MATCH_COUNT = 20


def get_champion_mapping():
    versions = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()
    latest = versions[0]
    champions = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{latest}/data/en_US/champion.json").json()
    return {int(data["key"]): name for name, data in champions["data"].items()}


def main():
    if not RIOT_API_KEY:
        raise ValueError("RIOT_API_KEY environment variable not set")

    headers = {"X-Riot-Token": RIOT_API_KEY}

    try:
        # Get PUUID
        account_url = 'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Autumn/Zico?api_key=RGAPI-c9d91c19-4894-4e8e-87e5-fb722f27cd7c'
        response = requests.get(account_url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        account_data = response.json()

        if 'puuid' not in account_data:
            print("Error: PUUID not found in response!")
            print("API Response:", account_data)
            return

        puuid = account_data["puuid"]

        # Rest of the code remains the same...
        # [Keep the match fetching and markdown generation code here]

    except HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response content: {e.response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()