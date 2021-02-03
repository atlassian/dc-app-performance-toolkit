import csv
from pathlib import Path
from typing import List

from scripts.utils import validate_str_is_not_blank, validate_file_exists, resolve_path

RESULTS_CSV_FILE_NAME = "results.csv"


class ResultsCSV:

    def __init__(self, absolute_file_path, actions: list):
        self.absolute_file_path = absolute_file_path
        self.actions = actions


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
    # Append 'App-specific' header
    header.append('App-specific')

    return header


def __validate_count_of_actions(tests_results: List[ResultsCSV]):
    if any(len(tests_results[0].actions) != len(actions_count.actions) for actions_count in tests_results):
        for file in tests_results:
            print(f'Result file {file.absolute_file_path} has {len(file.actions)} actions\n')
        raise SystemExit('Incorrect number of actions. '
                         'The number of actions should be the same for each results.csv.')


def __get_tests_results(config: dict) -> List[ResultsCSV]:
    results_files_list = []
    column_name = config['column_name']
    for run in config['runs']:
        value_by_action = {}
        absolute_file_path = resolve_path(run['fullPath']) / RESULTS_CSV_FILE_NAME
        with absolute_file_path.open(mode='r') as fs:
            for row in csv.DictReader(fs):
                value_by_action[row['Label']] = {column_name:row[column_name], 'App-specific': row['App specific']}
            results_files_list.append(ResultsCSV(absolute_file_path=absolute_file_path, actions=value_by_action))

    return results_files_list


def __write_list_to_csv(header: List[str], tests_results: List[ResultsCSV], output_filename: Path, config: dict):
    actions = [action for action in tests_results[0].actions]

    with output_filename.open(mode='w', newline='') as file_stream:
        writer = csv.writer(file_stream)
        writer.writerow(header)
        for action in actions:
            row = [action] + \
                  [value_by_action.actions[action][config['column_name']] for value_by_action in tests_results] + \
                  [tests_results[0].actions[action]['App-specific']]

            writer.writerow(row)


def __get_output_file_path(config, results_dir) -> Path:
    return results_dir / f"{config['profile']}.csv"


def aggregate(config: dict, results_dir: Path) -> Path:
    __validate_config(config)
    tests_results = __get_tests_results(config)
    __validate_count_of_actions(tests_results)
    output_file_path = __get_output_file_path(config, results_dir)
    header = __create_header(config)
    __write_list_to_csv(header, tests_results, output_file_path, config)

    validate_file_exists(output_file_path, f"Result file {output_file_path} is not created")
    print(f'Results file {output_file_path.absolute()} is created')
    return output_file_path
