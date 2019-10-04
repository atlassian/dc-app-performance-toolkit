import datetime
import sys
from pathlib import Path

# Work around import issue
sys.path.insert(0, str(Path(__file__).absolute().parent))
print("System path: ", sys.path)

from scripts import config_provider, csv_aggregator, chart_generator


def main():
    results_dir = __get_results_dir()

    csv_aggregator_config = config_provider.get_csv_aggregator_config()
    agg_csv = csv_aggregator.aggregate(csv_aggregator_config, results_dir)
    chart_generator_config = config_provider.get_chart_generator_config(csv_aggregator_config, agg_csv)
    chart_generator.perform_chart_creation(chart_generator_config, results_dir)


def __get_results_dir() -> Path:
    path = (Path(__file__).absolute().parents[1] / "results" / "reports" /
            datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    path.mkdir(parents=True, exist_ok=True)
    return path


if __name__ == "__main__":
    main()
