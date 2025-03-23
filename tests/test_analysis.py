import pytest
from src.analysis.stat_analyser import StatAnalyzer
from src.models.schemas import PlayerStats


@pytest.fixture
def sample_stats():
    return PlayerStats(
        puuid="123",
        champion="Ahri",
        kills=5,
        deaths=2,
        assists=8,
        kda=6.5,
        cs_total=200,
        cs_per_min=7.5,
        vision_score=25,
        gold_per_min=450,
        damage_per_min=600,
        win=True,
        champion_id=103,
        lane="MIDDLE"
    )


class TestStatAnalyzer:
    def setup_method(self):
        self.analyzer = StatAnalyzer()
        self.stats1 = PlayerStats(win=True, kills=5, deaths=1, assists=3, cs_per_min=8.0)
        self.stats2 = PlayerStats(win=False, kills=2, deaths=4, assists=1, cs_per_min=6.5)

    def test_initial_state(self):
        assert len(self.analyzer.matches) == 0
        assert len(self.analyzer.get_champion_matchups()) == 0

    def test_add_match(self):
        self.analyzer.add_match(self.stats1, self.stats2)
        assert len(self.analyzer.matches) == 1

    def test_win_rate_calculation(self):
        self.analyzer.add_match(self.stats1, self.stats2)  # Win
        self.analyzer.add_match(self.stats2, self.stats1)  # Loss
        assert self.analyzer.get_win_rate() == 0.5

    def test_average_stats(self):
        self.analyzer.add_match(self.stats1, self.stats2)
        self.analyzer.add_match(self.stats2, self.stats1)
        averages = self.analyzer.get_average_stats()
        assert averages['kills'] == 3.5
        assert averages['cs_per_min'] == 7.25

    def test_champion_matchups(self, sample_stats):
        opponent = PlayerStats(win=False, champion="Zed")
        self.analyzer.add_match(sample_stats, opponent)
        matchups = self.analyzer.get_champion_matchups()
        assert "Ahri_vs_Zed" in matchups