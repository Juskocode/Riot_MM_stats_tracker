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

def request_match_list_api(puuid, start, gamesToCheck):
    url = f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids'
    url_params = url + '?start=' + str(start) + '&count=' + str(gamesToCheck)
    api_url = url_params + '&api_key=' + os.getenv('RIOT_API_KEY')
    get_request = requests.get(api_url)
    data = get_request.json()
    return data

def request_match_api(matchId):
    url = f'https://europe.api.riotgames.com/lol/match/v5/matches/'
    url_params = url + str(matchId)
    api_url = url_params + '?api_key=' + os.getenv('RIOT_API_KEY')
    get_request = requests.get(api_url)
    game_data = get_request.json()
    return game_data

def process_match_api(match_data):
    pass

def process_match_list_api(matches_data):
    pass

def generate_markdown_table(processed_data):
    pass

def write_markdown_file(markdown_data):
    pass

def main():
    puuid = request_puuid_summoner_api("Autumn", "Zico")
    print(f'puuid = {puuid}')
    matches = request_match_list_api(puuid, 0, 20)
    print(f'matches = {matches}')
    match_data = request_match_api(matches[0])
    print(f'match = {match_data}')

if __name__ == "__main__":
    main()