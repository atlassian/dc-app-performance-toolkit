import datetime
from pathlib import Path

from scripts import (config_provider, csv_aggregator, chart_generator,
                     summary_aggregator, results_archivator)


def main():
    config = config_provider.get_config()
    product_name = summary_aggregator.__get_product_name(config)
    results_dir = __get_results_dir(config, product_name)

    agg_csv = csv_aggregator.aggregate(config, results_dir)
    agg, scenario_status = summary_aggregator.aggregate(config, results_dir)
    chart_generator_config = config_provider.get_chart_generator_config(config, agg_csv)
    chart_generator.perform_chart_creation(chart_generator_config, results_dir, scenario_status)
    results_archivator.archive_results(config, results_dir)


def __get_results_dir(config, product_name) -> Path:
    path = (Path(__file__).absolute().parents[1] / "results" / "reports" /
            f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{product_name}_{config['profile']}")
    print(f"Results dir: {path}")
    path.mkdir(parents=True, exist_ok=True)
    return path


if __name__ == "__main__":
    main()
