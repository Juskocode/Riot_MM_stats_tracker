import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

SUMMONER_NAME = "Autumn"
TAG_LINE = "Zico"
REGION = "euw"
MATCH_COUNT = 20


def get_opgg_url():
    formatted_name = f"{SUMMONER_NAME}-{TAG_LINE}"
    encoded_name = quote(formatted_name)
    return f"https://www.op.gg/summoners/{REGION}/{encoded_name}"


def extract_match_data(soup):
    matches = []
    game_tables = soup.find_all('div', class_='space-y-2')

    for game in game_tables[:MATCH_COUNT]:
        # Find player's team (look for Victory/Defeat)
        result_div = game.find('span', class_='font-bold')
        if not result_div:
            continue

        result = "Victory" if "Victory" in result_div.text else "Defeat"
        team_table = game.find('th', string=lambda t: t and "Victory" in t).find_parent(
            'table') if result == "Victory" else game.find('th', string=lambda t: t and "Defeat" in t).find_parent(
            'table')

        # Find player row
        player_row = team_table.find('a', string=SUMMONER_NAME).find_parent('tr')

        # Extract data
        champion = player_row.find('img', alt=True)['alt']
        kda = player_row.find('span', class_='leading-[14px]').text
        cs = player_row.find('div', class_='text-center').text
        items = [img['alt'] for img in player_row.select('img[alt]') if
                 'Summoner' not in img['alt'] and 'perk' not in img['alt']]
        vision = player_row.find('div', class_='text-center').find_next_sibling('div').text

        matches.append({
            'champion': champion,
            'result': result,
            'kda': kda,
            'cs': cs,
            'items': ', '.join(items[:6]),  # Only first 6 items
            'vision': vision.split('/')[0].strip(),
            'duration': game.find('div', class_='game-length').text if game.find('div', class_='game-length') else 'N/A'
        })

    return matches


def generate_markdown(matches):
    markdown = [
        "| Champion | Result | KDA | CS | Vision | Items | Died to Gank? | Notes |",
        "|----------|--------|-----|----|--------|-------|---------------|-------|"
    ]

    for match in matches:
        row = [
            f"**{match['champion']}**",
            "✔️" if match['result'] == "Victory" else "❌",
            match['kda'],
            match['cs'],
            match['vision'],
            match['items'],
            "- [ ]",  # Gank checkbox
            ""  # Notes
        ]
        markdown.append("|" + "|".join(row) + "|")

    return "\n".join(markdown)


def main():
    try:
        url = get_opgg_url()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        matches = extract_match_data(soup)

        with open("Autumn_Games.md", "w") as f:
            f.write(generate_markdown(matches))

        print(f"Successfully generated {len(matches)} games in Autumn_Games.md")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()