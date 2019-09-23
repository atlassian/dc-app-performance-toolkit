import csv
from pathlib import Path
from typing import List

from scripts.utils import validate_str_is_not_blank, validate_file_exists, resolve_path

RESULTS_CSV_FILE_NAME = "results.csv"


def __validate_config(config: dict):
    validate_str_is_not_blank(config, 'column_name')
    validate_str_is_not_blank(config, 'profile')

    runs = config.get('runs')
    if not isinstance(runs, list):
        raise SystemExit(f'Config key "runs" should be a list')

    for run in runs:
        if not isinstance(run, dict):
            raise SystemExit(f'Config key "run" should be a dictionary')

        validate_str_is_not_blank(run, 'runName')
        validate_str_is_not_blank(run, 'fullPath')


def __create_header(config) -> List[str]:
    header = ['Action']
    [header.append(run['runName']) for run in config['runs']]

    return header


def __validate_count_of_actions(key_files: dict):
    # TODO consider doing validation and reading file avoiding opening the same file two times (see __get_data_to_write)
    counter = 0
    counter_dict = {}
    for run in key_files['runs']:
        filename = resolve_path(run['fullPath']) / RESULTS_CSV_FILE_NAME
        with filename.open(mode='r') as f:
            records = csv.DictReader(f)
            row_count = sum(1 for _ in records)
            counter_dict[filename] = row_count
            if counter == 0:
                counter = row_count
            if row_count != counter:
                for filename, actions in counter_dict.items():
                    print(f'Result file {filename} has {actions} actions\n')
                raise SystemExit('Incorrect number of actions. '
                                 'The number of actions should be the same for each results.csv.')


def __get_data_to_write(config: dict) -> List[dict]:
    __validate_count_of_actions(config)

    column_value_by_label_list = []
    column_name = config['column_name']
    for run in config['runs']:
        column_value_by_label = {}
        filename = resolve_path(run['fullPath']) / RESULTS_CSV_FILE_NAME
        with filename.open(mode='r') as fs:
            for row in csv.DictReader(fs):
                column_value_by_label[row['Label']] = row[column_name]
        column_value_by_label_list.append(column_value_by_label)

    return column_value_by_label_list


def __write_list_to_csv(header: List[str], rows: List[dict], output_filename: Path):
    first_file_labels = rows[0].keys()
    with output_filename.open(mode='w', newline='') as file_stream:
        writer = csv.writer(file_stream)
        writer.writerow(header)
        for label in first_file_labels:
            row = [label] + [column_value_by_label[label] for column_value_by_label in rows]
            writer.writerow(row)


def __get_output_file_path(config, results_dir) -> Path:
    return results_dir / f"{config['profile']}.csv"


def aggregate(config: dict, results_dir: Path) -> Path:
    __validate_config(config)
    output_file_path = __get_output_file_path(config, results_dir)
    header = __create_header(config)
    data = __get_data_to_write(config)
    __write_list_to_csv(header, data, output_file_path)

    validate_file_exists(output_file_path, f"Result file {output_file_path} is not created")
    print(f'Results file {output_file_path.absolute()} is created')
    return output_file_path
