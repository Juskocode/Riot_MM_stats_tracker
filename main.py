from config import Settings
from src.api.riot_client import RiotAPIClient
from src.processing.match_processor import MatchProcessor
from src.analysis.stat_analyser import StatAnalyzer
from src.reporting.report_genorator import ReportGenerator
from src.visualization.plot_generator import PlotGenerator
from pydantic import ValidationError

def main():
    try:
        # Initialize configuration
        settings = Settings()
    except ValidationError as e:
        print(f"Configuration error: {e}")
        print("Please check your .env file")
        return
    api_client = RiotAPIClient(settings)
    processor = MatchProcessor()
    analyzer = StatAnalyzer()
    plotter = PlotGenerator()
    plotter.kda_distribution(analyzer)
    plotter.cs_per_min_timeline(analyzer)
    reporter = ReportGenerator()

    # Fetch player data
    puuid = api_client.get_puuid("Autumn", "Zico")
    if not puuid:
        print("Failed to retrieve PUUID")
        return
    else:
        print(f"Player PUUID: {puuid}")
    # Process matches
    match_ids = api_client.get_match_ids(puuid, count=100)
    print(match_ids)
    for match_id in match_ids:
        match_data = api_client.get_match_data(match_id)
        print(f"Processing match {match_id}")
        if match_data:
            processed = processor.process_match(match_data, puuid)
            if processed:
                print(f"went done {match_id}")
                analyzer.add_match(*processed)

    # Generate and save report
    reporter.generate_full_report(analyzer.matches, analyzer)

if __name__ == "__main__":
    main()