import pytest
from unittest.mock import Mock, patch
from src.api.riot_client import RiotAPIClient
from config import Settings


@pytest.fixture
def mock_settings():
    return Settings(RIOT_API_KEY="test_key")


class TestRiotAPIClient:
    @patch('requests.Session')
    def test_get_puuid_success(self, mock_session, mock_settings):
        mock_response = Mock()
        mock_response.json.return_value = {"puuid": "test_puuid"}
        mock_session.return_value.get.return_value = mock_response

        client = RiotAPIClient(mock_settings)
        puuid = client.get_puuid("TestUser", "Tag")
        assert puuid == "test_puuid"

    @patch('requests.Session')
    def test_get_puuid_failure(self, mock_session, mock_settings):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_session.return_value.get.return_value = mock_response

        client = RiotAPIClient(mock_settings)
        puuid = client.get_puuid("TestUser", "Tag")
        assert puuid is None

    @patch('requests.Session')
    def test_get_match_data(self, mock_session, mock_settings):
        mock_response = Mock()
        mock_response.json.return_value = {"match_id": "TEST123"}
        mock_session.return_value.get.return_value = mock_response

        client = RiotAPIClient(mock_settings)
        data = client.get_match_data("TEST123")
        assert data == {"match_id": "TEST123"}