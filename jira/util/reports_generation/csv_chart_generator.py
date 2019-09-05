import sys
from pathlib import Path

import os
sys.path.insert(0, os.path.dirname(os.getcwd()))
filpath = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, str(Path(filpath).parents[2]))
print("System path: ", sys.path)

import jira.util.reports_generation.chart_generator.chart_generator as chart_generator
import jira.util.reports_generation.csv_aggregator.csv_aggregator as csv_aggregator


def create_csv_aggregated_report(configs: dict, output_file_csv):
    header = csv_aggregator.__create_header(configs)
    data_to_csv = csv_aggregator.get_data_to_write(config=configs)
    csv_aggregator.write_list_to_csv(list_to_write=data_to_csv, output_filename=output_file_csv, columns=header)
    csv_aggregator.__validate_file_exists(output_file_csv, f"Result file {output_file_csv} is not created")
    print(f'Results file {output_file_csv} is created')


def create_chart(configs, aggregated_csv):
    chart_generator.__validate_is_not_blank(configs, "index_col")
    chart_generator.__validate_is_not_blank(configs, "title")
    chart_generator.__validate_is_number(configs, "image_height_px")
    chart_generator.__validate_is_number(configs, "image_width_px")
    title = Path(aggregated_csv).stem
    chart_generator.make_chart(aggregated_csv, configs["index_col"], title, configs["image_height_px"],
                               configs["image_width_px"])


def main():
    config_file = csv_aggregator.__get_config_file()
    configs = csv_aggregator.read_validate_config(config_file)
    output_file_csv = csv_aggregator.get_output_filename(config_file, configs)
    create_csv_aggregated_report(configs, output_file_csv)

    create_chart(configs, output_file_csv)


if __name__ == "__main__":
    main()
