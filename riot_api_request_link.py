import requests
import os
from requests.exceptions import HTTPError
from dotenv import load_dotenv

load_dotenv()

def request_puuid_summoner_api(tagline, gameName):
    url = f'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{tagline}/{gameName}'
    api_url = url + '?api_key=' + os.getenv('RIOT_API_KEY')
    get_request = requests.get(api_url)
    data = get_request.json()
    return data['puuid']

def request_matchid_list_api(puuid, start, gamesToCheck):
    url = f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids'
    url_params = url + '?start=' + str(start) + '&count=' + str(gamesToCheck)
    api_url = url_params + '&api_key=' + os.getenv('RIOT_API_KEY')
    get_request = requests.get(api_url)
    data = get_request.json()
    return data

def request_match_data(matchId):
    url = f'https://europe.api.riotgames.com/lol/match/v5/matches/'
    url_params = url + str(matchId)
    api_url = url_params + '?api_key=' + os.getenv('RIOT_API_KEY')
    get_request = requests.get(api_url)
    game_data = get_request.json()
    return game_data

def process_player_data(match_data, puuid):
    player_index = match_data['metadata']['participants'].index(puuid)
    return match_data['info']['participants'][player_index]

def process_match_list_api(matches_data, puuid):
    matches_data = []
    for match in matches_data:
        matches_data.append(process_player_data(match, puuid))
    return matches_data

def extract_player_stats(match_player_data):
    # Extract main stats from the match_player_data dictionary
    total_time_minutes = match_player_data.get('timePlayed', 1) / 60
    total_cs = match_player_data.get('totalMinionsKilled', 0) + match_player_data.get('neutralMinionsKilled', 0)
    stats = {
        'champion': match_player_data.get('championName', 0),
        'lane': match_player_data.get('lane', 'N/A'),
        'kills': match_player_data.get('kills', 0),
        'deaths': match_player_data.get('deaths', 0),
        'assists': match_player_data.get('assists', 0),
        'kda' : match_player_data.get('kda', 0),
        'creep_score': total_cs,
        'creep_score_per_minute': total_cs / total_time_minutes if total_time_minutes > 0 else 0,
        'vision_score': match_player_data.get('visionScore', 0),
        'goldPerMinute': match_player_data.get('challenges', {}).get('goldPerMinute', 0),
        'damage_per_minute': match_player_data.get('challenges', {}).get('damagePerMinute', 0),
        'ganked': match_player_data.get('challenges', {}).get('killsOnLanersEarlyJungleAsJungler', 0),
        # Assuming "ganked" tracks early kills on laners as a jungler
    }
    return stats

def extract_player_stats_all(matches_data):
    player_stats = []
    for match in matches_data:
        player_stats.append(extract_player_stats(match))
    return player_stats

def generate_markdown_table(processed_data):
    if not processed_data:
        return "No data available to display in the table."

    # Extract the table headers from the first dictionary's keys
    headers = list(processed_data[0].keys())

    # Start building the Markdown table
    markdown_table = []

    # Add the headers row
    markdown_table.append("| " + " | ".join(headers) + " |")

    # Add the separator for the headers
    markdown_table.append("| " + " | ".join(["---"] * len(headers)) + " |")

    # Add rows for each entry in processed_data
    for game_stats in processed_data:
        row = "| " + " | ".join(str(game_stats.get(header, "")) for header in headers) + " |"
        markdown_table.append(row)

    # Join the table rows with newline characters
    return "\n".join(markdown_table)


def write_markdown_file(markdown_data):
    file_name = "player_stats.md"
    try:
        with open(file_name, "w") as file:
            file.write(markdown_data)
        print(f"Markdown file {file_name} created successfully.")
    except Exception as e:
        print(f"An error occurred while writing the markdown file: {e}")

def write_markdown_obsidian(markdown_data, file_name="player_stats.md", title=None, tags=None):
    try:
        with open(file_name, "w") as file:
            # Add a title if provided
            if title:
                file.write(f"# {title}\n\n")

            # Write the markdown table to the file
            file.write(markdown_data + "\n\n")

            # Add tags if provided
            if tags:
                formatted_tags = " ".join(f"#{tag}" for tag in tags)
                file.write(f"Tags: {formatted_tags}\n")

        print(f"Obsidian-compatible markdown file '{file_name}' created successfully.")
    except Exception as e:
        print(f"An error occurred while writing the markdown file: {e}")


def extract_opposing_player_data(match_data, current_puuid):
    """
    Extract the stats of the player in the same lane on the opposite team.

    :param match_data: Match data containing players' stats.
    :param current_puuid: The current player's PUUID.
    :return: Dictionary with the opposite player's stats or an empty dictionary if no match is found.
    """
    # Identify the participant that matches the current PUUID
    participants = match_data['info']['participants']
    current_player = next(player for player in participants if player['puuid'] == current_puuid)

    # Get the lane of the current player
    current_lane = current_player.get('teamPosition', 'UNKNOWN')

    # Find the opposing team's players
    opposing_team = [player for player in participants if player['teamId'] != current_player['teamId']]

    # Identify the opposing player in the same lane
    opposing_player = next(
        (player for player in opposing_team if player.get('teamPosition', '') == current_lane),
        None
    )

    return opposing_player if opposing_player else {}

def generate_markdown_table_with_opponents(processed_data):
    """
    Generate a markdown table comparing current player's stats with opposing laner stats.

    :param processed_data: List of tuples (player_stats, opposing_stats) for each match.
    :return: A string containing the markdown table.
    """
    if not processed_data:
        return "No data available to display in the table."

    # Define headers for the main stats table with an extra "Champion vs" column
    headers = [
        "Champion vs",
        "kills", "deaths", "assists", "kda",
        "creep_score", "creep_score_per_minute",
        "vision_score", "goldPerMinute", "damage_per_minute"
    ]

    # Build the table
    markdown_table = []
    markdown_table.append("| " + " | ".join(headers) + " |")
    markdown_table.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for player_stats, opposing_stats in processed_data:
        champion_vs = f"{player_stats['champion']} (you) vs {opposing_stats['champion'] if opposing_stats else 'N/A'}"
        row = [
            champion_vs,
            player_stats.get('kills', 0), player_stats.get('deaths', 0), player_stats.get('assists', 0),
            player_stats.get('kda', 0),
            player_stats.get('creep_score', 0), player_stats.get('creep_score_per_minute', 0),
            player_stats.get('vision_score', 0), player_stats.get('goldPerMinute', 0),
            player_stats.get('damage_per_minute', 0)
        ]
        markdown_table.append("| " + " | ".join(map(str, row)) + " |")

    return "\n".join(markdown_table)

def generate_laner_comparison_table(processed_data):
    """
    Generate a markdown table comparing the stats of the current player against their opposing laner for all matches.

    :param processed_data: List of tuples (player_stats, opposing_stats) for each match.
    :return: A string containing the markdown table for laner vs laner comparison.
    """
    if not processed_data:
        return "No data available to display in the table."

    # Define headers for the comparison table
    headers = [
        "Stat", "Your Value", "Opponent's Value"
    ]

    # Build the comparison table row by row
    markdown_table = []
    markdown_table.append("| " + " | ".join(headers) + " |")
    markdown_table.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for player_stats, opposing_stats in processed_data:
        if not opposing_stats:
            continue  # Skip if no opposing stats are available

        comparison_data = [
            ("Kills", player_stats.get('kills', 0), opposing_stats.get('kills', 0)),
            ("Deaths", player_stats.get('deaths', 0), opposing_stats.get('deaths', 0)),
            ("Assists", player_stats.get('assists', 0), opposing_stats.get('assists', 0)),
            ("KDA", player_stats.get('kda', 0), opposing_stats.get('kda', 0)),
            ("Creep Score", player_stats.get('creep_score', 0), opposing_stats.get('creep_score', 0)),
            ("Creep Score Per Minute", player_stats.get('creep_score_per_minute', 0),
             opposing_stats.get('creep_score_per_minute', 0)),
            ("Vision Score", player_stats.get('vision_score', 0), opposing_stats.get('vision_score', 0)),
            ("Gold Per Minute", player_stats.get('goldPerMinute', 0), opposing_stats.get('goldPerMinute', 0)),
            ("Damage Per Minute", player_stats.get('damage_per_minute', 0), opposing_stats.get('damage_per_minute', 0))
        ]

        for stat, your_value, opponent_value in comparison_data:
            markdown_table.append(f"| {stat} | {your_value} | {opponent_value} |")

        # Add a separator row between matches
        markdown_table.append("| --- | --- | --- |")

    return "\n".join(markdown_table)


def process_player_and_opposing_data(match_data, current_puuid):
    """
    Process and extract data for the current player and the opposing player in the same lane.

    :param match_data: Match data for a single game.
    :param current_puuid: The current player's PUUID.
    :return: Tuple containing the current player's stats and the opposing laner's stats.
    """
    current_player_data = extract_player_stats(
        match_data['info']['participants'][match_data['metadata']['participants'].index(current_puuid)])
    opposing_player_data = extract_player_stats(extract_opposing_player_data(match_data, current_puuid))
    return current_player_data, opposing_player_data


def main():
    # request puuid of player
    puuid = request_puuid_summoner_api("Autumn", "Zico")
    #print(f'puuid = {puuid}')
    # last  games ids (including non ranked)
    matches = request_matchid_list_api(puuid, 0, 10)
    #print(f'matches = {matches}')
    # Process match data
    processed_stats = []
    for match in matches:
        match_data = request_match_data(match)
        processed_stats.append(process_player_and_opposing_data(match_data, puuid))

    # Generate markdown tables
    main_table = generate_markdown_table_with_opponents(processed_stats)
    laner_comparison_table = generate_laner_comparison_table(processed_stats)

    # Combine both tables
    full_markdown = f"{main_table}\n\n# Laner vs Laner Comparison\n\n{laner_comparison_table}"

    # Write to an Obsidian-style markdown file
    write_markdown_obsidian(
        markdown_data=full_markdown,
        file_name="player_stats_comparison_obsidian.md",
        title="Player Stats and Laner Comparison",
        tags=["games", "stats", "LeagueOfLegends"]
    )
    '''
    # request match data
    matches_data = []
    for match in matches:
        matches_data.append(request_match_data(match))
    print(f'matches_data = {matches_data}')
    players_data = []
    for match_data in matches_data:
        players_data.append(process_player_data(match_data, puuid))
    print(f'players_data = {players_data}')
    # extract player stats from games
    player_stats = extract_player_stats_all(players_data)
    print(f'player_stats = {player_stats}')

    # Generate markdown table
    markdown_table = generate_markdown_table(player_stats)

    # Write table to a markdown file
    write_markdown_file(markdown_table)
    '''

if __name__ == "__main__":
    main()