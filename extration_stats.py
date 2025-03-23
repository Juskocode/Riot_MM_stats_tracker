import requests
import os
from requests.exceptions import HTTPError

# Configuration
RIOT_API_KEY = 'RGAPI-c788b0b6-ee60-4541-9389-1990e6556906'
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

    # Get PUUID
    account_url = 'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Autumn/Zico?api_key=RGAPI-c9d91c19-4894-4e8e-87e5-fb722f27cd7c'
    account_data = requests.get(account_url, headers=headers).json()
    puuid = account_data["puuid"]

    # Get match list
    matches_url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    match_ids = requests.get(matches_url, headers=headers, params={"count": MATCH_COUNT}).json()

    # Get champion mapping
    champion_map = get_champion_mapping()

    matches_data = []
    for match_id in match_ids:
        match = requests.get(f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}",
                             headers=headers).json()
        participant = next(p for p in match["info"]["participants"] if p["puuid"] == puuid)

        matches_data.append({
            "champion": champion_map.get(participant["championId"], "Unknown"),
            "win": "✔️" if participant["win"] else "❌",
            "kda": f"{participant['kills']}/{participant['deaths']}/{participant['assists']}",
            "cs": participant["totalMinionsKilled"] + participant["neutralMinionsKilled"],
            "vision": participant["visionScore"],
            "gold": f"{participant['goldEarned'] // 1000}k",
            "spells": [participant["summoner1Id"], participant["summoner2Id"]],
            "items": [participant[f"item{i}"] for i in range(6)],
            "duration": f"{match['info']['gameDuration'] // 60}:{match['info']['gameDuration'] % 60:02d}"
        })

    # Generate Markdown table
    markdown = [
        "| Champion | Result | K/D/A | CS | Vision | Gold | Duration | Died to Gank? | Notes |",
        "|----------|--------|-------|----|--------|------|----------|---------------|-------|"
    ]

    for game in matches_data:
        row = [
            f"**{game['champion']}**",
            game["win"],
            game["kda"],
            game["cs"],
            game["vision"],
            game["gold"],
            game["duration"],
            "- [ ]",  # Gank death checkbox
            ""  # Notes column
        ]
        markdown.append("|" + "|".join(map(str, row)) + "|")

    with open("Autumn_Games.md", "w") as f:
        f.write("\n".join(markdown))

    print(f"Successfully generated {len(matches_data)} games in Autumn_Games.md")


if __name__ == "__main__":
    main()