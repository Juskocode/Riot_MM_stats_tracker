import pytest
from src.processing.match_processor import MatchProcessor
from src.models.schemas import PlayerStats

@pytest.fixture
def sample_match_data():
    return {
        "metadata": {
            "participants": ["player1", "player2"]
        },
        "info": {
            "participants": [
                {
                    "puuid": "player1",
                    "championName": "Ahri",
                    "kills": 5,
                    "deaths": 2,
                    "assists": 8,
                    "challenges": {"kda": 6.5},
                    "totalMinionsKilled": 180,
                    "neutralMinionsKilled": 20,
                    "timePlayed": 1500,
                    "visionScore": 25,
                    "win": True,
                    "championId": 103,
                    "teamPosition": "MIDDLE"
                },
                {
                    "puuid": "player2",
                    "championName": "Zed",
                    "teamPosition": "MIDDLE"
                }
            ]
        }
    }

class TestMatchProcessor:
    def test_process_valid_match(self, sample_match_data):
        processor = MatchProcessor()
        result = processor.process_match(sample_match_data, "player1")
        assert result is not None
        player, opponent = result
        assert player.champion == "Ahri"
        assert opponent.champion == "Zed"

    def test_missing_opponent(self, sample_match_data):
        # Remove opponent's team position
        sample_match_data["info"]["participants"][1]["teamPosition"] = ""
        processor = MatchProcessor()
        result = processor.process_match(sample_match_data, "player1")
        assert result is None

    def test_invalid_match_data(self):
        processor = MatchProcessor()
        result = processor.process_match({}, "invalid_puuid")
        assert result is None

    def test_stats_calculation(self, sample_match_data):
        processor = MatchProcessor()
        player_stats, _ = processor.process_match(sample_match_data, "player1")
        assert player_stats.cs_total == 200  # 180 + 20
        assert player_stats.cs_per_min == pytest.approx(8.0)  # 200 / 25 min