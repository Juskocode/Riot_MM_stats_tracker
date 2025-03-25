import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

class PlotGenerator:
    def __init__(self, output_dir: str = "plots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        sns.set_theme(style="whitegrid")
        plt.rcParams["figure.figsize"] = (12, 8)

    def kda_distribution(self, analyser: "StatAnalyzer"):
        """Generate KDA distribution histogram"""
        plt.figure()
        kdas = [p.kda for p, _ in analyser.matches]
        sns.histplot(kdas, kde=True, bins=8)
        plt.title("🎯 KDA Distribution Across Matches")
        plt.xlabel("KDA Ratio")
        plt.ylabel("Number of Matches")
        self._save_plot("kda_distribution.png")

    def cs_per_min_timeline(self, analyzer: 'StatAnalyzer'):
        """Line plot of CS/min over matches"""
        plt.figure()
        cs_values = [p.cs_per_min for p, _ in analyzer.matches]
        plt.plot(cs_values, marker='o', linestyle='--')
        plt.title("📈 CS per Minute Timeline")
        plt.xlabel("Match Number")
        plt.ylabel("CS/min")
        self._save_plot("cs_timeline.png")

    def win_rate_by_lane(self, analyzer: 'StatAnalyzer'):
        """Bar chart of win rates by lane position"""
        plt.figure()
        lane_data = {}
        for p, _ in analyzer.matches:
            lane = p.lane
            lane_data.setdefault(lane, {'wins': 0, 'total': 0})
            lane_data[lane]['wins'] += int(p.win)
            lane_data[lane]['total'] += 1

        lanes = list(lane_data.keys())
        win_rates = [lane_data[lane]['wins'] / lane_data[lane]['total'] for lane in lanes]

        sns.barplot(x=lanes, y=win_rates, palette="viridis")
        plt.title("🏆 Win Rate by Lane Position")
        plt.ylabel("Win Rate")
        plt.ylim(0, 1)
        self._save_plot("win_rate_by_lane.png")

    def damage_composition_radar(self, analyzer: 'StatAnalyzer'):
        """Radar chart showing stats distribution"""
        plt.figure()
        categories = ['kda', 'cs_per_min']
        avg_stats = [
            np.mean([p.kda for p, _ in analyzer.matches]),
            np.mean([p.cs_per_min for p, _ in analyzer.matches]),
            np.mean([p.win for p, _ in analyzer.matches])
        ]

        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        fig = plt.figure()
        ax = fig.add_subplot(111, polar=True)
        ax.plot(angles, avg_stats, color='r', linewidth=2)
        ax.fill(angles, avg_stats, color='r', alpha=0.25)
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles)
        ax.set_xticklabels(categories)
        plt.title("🔥 stats Distribution")
        self._save_plot("stats_radar.png")

    def _save_plot(self, filename: str):
        """Internal method to save plots"""
        path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(path, bbox_inches='tight')
        plt.close()