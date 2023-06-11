import datetime
from pathlib import Path
from scripts import (config_provider, csv_aggregator, chart_generator,
                     summary_aggregator, results_archivator, judgement)
from util.jtl_convertor.jtls_to_csv import __get_all_default_actions, __convert_jtl_to_csv, __create_results_csv


def convert_jtl_files(config, cold_start):
    for run in config['runs']:
        temp_csv_list = []
        jtl_files = Path(run['fullPath']).glob('*.jtl')
        for jtl_file in jtl_files:
            temp_csv_path = jtl_file.with_suffix('.tmp.csv')
            default_test_actions = __get_all_default_actions()
            __convert_jtl_to_csv(jtl_file, temp_csv_path, default_test_actions, cold_start)
            temp_csv_list.append(temp_csv_path)

        results_file_path = Path(run['fullPath']) / 'results.csv'
        __create_results_csv(temp_csv_list, results_file_path)

        for temp_csv_path in temp_csv_list:
            temp_csv_path.unlink()


def process_results(config, results_dir):
    agg_csv = csv_aggregator.aggregate(config, results_dir)
    agg, scenario_status = summary_aggregator.aggregate(config, results_dir)
    chart_generator_config = config_provider.get_chart_generator_config(config, agg_csv)
    chart_generator.perform_chart_creation(chart_generator_config, results_dir, scenario_status)
    results_archivator.archive_results(config, results_dir)


def main():
    config = config_provider.get_config()
    results_dir = __get_results_dir()
    cold_start = config.get('cold_start', 0)

    convert_jtl_files(config, cold_start)

    process_results(config, results_dir)

    if config['judge']:
        judgement_kwargs = judgement.__get_judgement_kwargs(config)
        judgement_kwargs["output_dir"] = results_dir
        judgement.judge(**judgement_kwargs)


def __get_results_dir() -> Path:
    path = (Path(__file__).absolute().parents[1] / "results" / "reports" /
            datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    path.mkdir(parents=True, exist_ok=True)
    return path


if __name__ == "__main__":
    main()
