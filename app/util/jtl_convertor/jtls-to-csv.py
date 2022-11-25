import csv
import json
import os
import sys
import tempfile
import time
from glob import glob
from pathlib import Path
from typing import IO, List, Set

import pandas

from util.jtl_convertor import jtl_validator
from util.project_paths import ENV_TAURUS_ARTIFACT_DIR, DEFAULT_TEST_ACTIONS

LABEL = 'Label'
SAMPLES = '# Samples'
AVERAGE = 'Average'
MEDIAN = 'Median'
PERC_90 = '90% Line'
PERC_95 = '95% Line'
PERC_99 = '99% Line'
MIN = 'Min'
MAX = 'Max'
ERROR_RATE = 'Error %'
LABEL_JTL = 'label'
ELAPSED_JTL_TMP = 'elapsed_tmp'
ELAPSED_JTL = 'elapsed'
SUCCESS_JTL = 'success'
SUCCESS_JTL_TMP = 'success_tmp'
FALSE_JTL = 'false'
APP_SPECIFIC = 'App specific'

CSV_HEADER = f'{LABEL},{SAMPLES},{AVERAGE},{MEDIAN},{PERC_90},{PERC_95},{PERC_99},{MIN},{MAX},{ERROR_RATE},' \
             f'{APP_SPECIFIC}\n'
RESULTS_CSV_NAME = 'results.csv'
APPS = ['jira', 'confluence', 'bitbucket', 'jsm', 'crowd', 'bamboo']
TEST_TYPES = ['selenium', 'jmeter', 'locust']


def __get_all_default_actions():
    full_actions_list = []
    actions_data = read_json_file(DEFAULT_TEST_ACTIONS)
    for app in APPS:
        for test_type in TEST_TYPES:
            for action in actions_data[app][test_type]:
                full_actions_list.append(action)
    return full_actions_list


def read_json_file(file_path):
    with open(file_path) as json_file:
        data = json.load(json_file)
        return data


def __count_file_lines(stream: IO) -> int:
    return sum(1 for _ in stream)


def __reset_file_stream(stream: IO) -> None:
    stream.seek(0)


def __convert_jtl_to_csv(input_file_path: Path, output_file_path: Path, default_test_actions: list) -> None:
    if not input_file_path.exists():
        raise SystemExit(f'ERROR: Input file {output_file_path} does not exist')
    start = time.time()
    convert_to_csv(output_csv=output_file_path, input_jtl=input_file_path, default_test_actions=default_test_actions)
    if not output_file_path.exists():
        raise SystemExit(f'ERROR: Something went wrong. Output file {output_file_path} does not exist')

    print(f'Created file {output_file_path}. Converted from jtl to csv in {time.time() - start} ')


def __change_file_extension(file_name: str, new_extension) -> str:
    return __get_file_name_without_extension(file_name) + new_extension


def __get_file_name_without_extension(file_name):
    return os.path.splitext(file_name)[0]


def __read_csv_without_first_line(results_file_stream, input_csv):
    with input_csv.open(mode='r') as file_stream:
        __reset_file_stream(file_stream)

        for cnt, line in enumerate(file_stream, 1):
            if cnt != 1:
                results_file_stream.write(line)
    print(f'File {input_csv} successfully read')


def __create_results_csv(csv_list: List[Path], results_file_path: Path) -> None:
    with results_file_path.open(mode='w') as results_file_stream:
        results_file_stream.write(CSV_HEADER)

        for temp_csv_path in csv_list:
            __read_csv_without_first_line(results_file_stream, temp_csv_path)

    if not results_file_path.exists():
        raise SystemExit(f'ERROR: Something went wrong. Output file {results_file_path} does not exist')
    print(f'Created file {results_file_path}')


def __validate_file_names(file_names: List[str]):
    file_names_set: Set[str] = set()

    for file_name in file_names:
        if '.' not in file_name:
            raise SystemExit(f'ERROR: File name {file_name} does not have extension')

        file_name_without_extension = __get_file_name_without_extension(file_name)
        if file_name_without_extension in file_names_set:
            raise SystemExit(f'ERROR: Duplicated file name {file_name_without_extension}')

        file_names_set.add(file_name_without_extension)


def __validate_file_length(file_names: List[str]):
    for file_name in file_names:
        lines_count = sum(1 for _ in open(ENV_TAURUS_ARTIFACT_DIR / file_name))
        if lines_count <= 1:
            raise SystemExit(f'ERROR: File {ENV_TAURUS_ARTIFACT_DIR / file_name} does not have content.\n'
                             f'See logs for detailed error: {ENV_TAURUS_ARTIFACT_DIR}')


def __pathname_pattern_expansion(args: List[str]) -> List[str]:
    file_names: List[str] = []
    for arg in args:
        file_names.extend([os.path.basename(x) for x in glob(str(ENV_TAURUS_ARTIFACT_DIR / arg))])
    return file_names


def convert_to_csv(input_jtl: Path, output_csv: Path, default_test_actions: list):
    # TODO: If list is too big, read iteratively from CSV if possible
    with input_jtl.open(mode='r') as f:
        reader = csv.DictReader(f)
        jtl_list = [row for row in reader]

    csv_list = []

    for jtl_sample in jtl_list:
        sample = {}
        if jtl_sample[LABEL_JTL] not in [processed_sample[LABEL] for processed_sample in csv_list]:
            sample[LABEL] = jtl_sample[LABEL_JTL]
            sample[SAMPLES] = 1
            sample[ELAPSED_JTL_TMP] = [int(jtl_sample[ELAPSED_JTL])]  # Temp list with 'elapsed' value for current label
            # Temp list with 'success' value for current label
            sample[SUCCESS_JTL_TMP] = [jtl_sample[SUCCESS_JTL].lower()]
            csv_list.append(sample)

        else:
            # Get and update processed row with current label
            processed_sample = [row for row in csv_list if row[LABEL] == jtl_sample['label']][0]
            processed_sample[SAMPLES] = processed_sample[SAMPLES] + 1  # Count samples
            processed_sample[ELAPSED_JTL_TMP].append(int(jtl_sample[ELAPSED_JTL]))  # list of elapsed values
            processed_sample[SUCCESS_JTL_TMP].append(jtl_sample[SUCCESS_JTL].lower())  # list of success values

    # Calculation after the last row in kpi.jtl is processed
    for processed_sample in csv_list:
        elapsed_df = pandas.Series(processed_sample[ELAPSED_JTL_TMP])
        processed_sample[AVERAGE] = int(round(elapsed_df.mean()))
        processed_sample[MEDIAN] = int(round(elapsed_df.quantile(0.5)))
        processed_sample[PERC_90] = int(round(elapsed_df.quantile(0.9)))
        processed_sample[PERC_95] = int(round(elapsed_df.quantile(0.95)))
        processed_sample[PERC_99] = int(round(elapsed_df.quantile(0.99)))
        processed_sample[MIN] = min(processed_sample[ELAPSED_JTL_TMP])
        processed_sample[MAX] = max(processed_sample[ELAPSED_JTL_TMP])
        success_list = processed_sample[SUCCESS_JTL_TMP]
        processed_sample[ERROR_RATE] = round(success_list.count(FALSE_JTL) / len(success_list), 2) * 100.00
        processed_sample[APP_SPECIFIC] = processed_sample['Label'] not in default_test_actions
        del processed_sample[SUCCESS_JTL_TMP]
        del processed_sample[ELAPSED_JTL_TMP]

    headers = csv_list[0].keys()
    with output_csv.open('w') as output_file:
        dict_writer = csv.DictWriter(output_file, headers)
        dict_writer.writeheader()
        for row in csv_list:
            dict_writer.writerow(row)


def main():
    args = sys.argv[1:]
    file_names = __pathname_pattern_expansion(args)
    __validate_file_names(file_names)
    __validate_file_length(file_names)

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_csv_list: List[Path] = []
        for file_name in file_names:
            jtl_file_path = ENV_TAURUS_ARTIFACT_DIR / file_name
            jtl_validator.validate(jtl_file_path)
            csv_file_path = Path(tmp_dir) / __change_file_extension(file_name, '.csv')
            default_test_actions = __get_all_default_actions()
            __convert_jtl_to_csv(jtl_file_path, csv_file_path, default_test_actions)
            temp_csv_list.append(csv_file_path)

        results_file_path = ENV_TAURUS_ARTIFACT_DIR / RESULTS_CSV_NAME
        __create_results_csv(temp_csv_list, results_file_path)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f'Done in {time.time() - start_time} seconds')
