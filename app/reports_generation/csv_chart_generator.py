import datetime
from pathlib import Path

from scripts import config_provider, csv_aggregator, chart_generator, summary_aggregator


def main():
    results_dir = __get_results_dir()

    config = config_provider.get_config()
    agg_csv = csv_aggregator.aggregate(config, results_dir)
    chart_generator_config = config_provider.get_chart_generator_config(config, agg_csv)
    chart_generator.perform_chart_creation(chart_generator_config, results_dir)
    summary_aggregator.aggregate(config, results_dir)


def __get_results_dir() -> Path:
    path = (Path(__file__).absolute().parents[1] / "results" / "reports" /
            datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    path.mkdir(parents=True, exist_ok=True)
    return path


if __name__ == "__main__":
    main()
