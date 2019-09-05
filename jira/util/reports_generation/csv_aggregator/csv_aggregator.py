import csv
import os
import sys
from pathlib import Path
from time import gmtime, strftime
import yaml


def __resolve_and_expand_user_path(path):
    return path.resolve().expanduser()


def read_validate_config(configfile: str):
    config_file = __resolve_and_expand_user_path(Path(configfile))
    __validate_file_exists(config_file, f"Config file {config_file} does not exist")
    with open(config_file, 'r') as file:
        report_yaml = yaml.load(file, Loader=yaml.FullLoader)
        for dict in report_yaml['runs']:
            result_dir = __get_config_value(dict, 'fullPath')
            __get_config_value(dict, 'runName')
            result_file = Path(result_dir) / Path("results.csv")
            __validate_file_exists(result_file, f'results.csv file in directory {dict["fullPath"]} does not exist')
        return report_yaml


def __create_header(config):
    row_header = ['Action']
    config_headers = [dict['runName'] for dict in config['runs']]
    row_header.extend(config_headers)
    return row_header


def get_output_filename(configfile: str, configs: dir):
    result_dir = Path(configs['runs'][0]['fullPath']).parents[0]
    os.makedirs(Path(result_dir / Path("reports")), exist_ok=True)
    output_filename = f'{result_dir}/reports/{Path(configfile).stem}_{strftime("%Y-%m-%d-%H-%M-%S", gmtime())}.csv'
    return output_filename


def __validate_file_exists(file, msg):
    if not os.path.exists(file):
        raise SystemExit(msg)


def __get_config_value(dict: dict, key):
    value = dict.get(key)
    if (value is None) or (not value.strip()):
        raise SystemExit(f"Config does not contain {key}")
    return value


def __validate_count_of_actions(key_files: dict):
    counter = 0
    counter_dict = {}
    for dict in key_files['runs']:
        filename = Path(dict['fullPath']) / "results.csv"
        with open(filename, 'r') as f:
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


def __get_config_file():
    config_file = ''.join(sys.argv[1:])
    if len(config_file) > 0 and config_file.endswith('.yml'):
        return os.path.basename(config_file)
    else:
        raise SystemExit('report.yml file cannot be undefined. '
                         'Run python util/csv_merger.py [scale_profile.yml or performance_profile.yml]')


def get_data_to_write(config: dict):
    list_to_csv = []
    __validate_count_of_actions(config)
    extract_column_name = config['column_name']
    for dict in config['runs']:
        data = {}
        filename = Path(dict['fullPath']) / "results.csv"
        with open(filename, 'r') as f:
            records = csv.DictReader(f)
            for row in records:
                key = row['Label']
                value = row[extract_column_name]
                data[key] = value
        list_to_csv.append(data)
    return list_to_csv


def write_list_to_csv(list_to_write: list, output_filename: str, columns):
    csv_columns = columns
    first_file_labels = list_to_write[0].keys()
    with open(output_filename, mode='w', newline='') as file_stream:
        writer = csv.writer(file_stream)
        writer.writerow(csv_columns)
        for label in first_file_labels:
            row = [label] + [column_value_by_label[label] for column_value_by_label in list_to_write]
            writer.writerow(row)


def main():
    config_file = __get_config_file()

    configs = read_validate_config(config_file)
    output_file = get_output_filename(config_file, configs)
    header = __create_header(configs)

    data_to_csv = get_data_to_write(config=configs)
    write_list_to_csv(list_to_write=data_to_csv, output_filename=output_file, columns=header)
    __validate_file_exists(output_file, f"Result file {output_file} is not created")
    print(f'Results file {output_file} is created')


if __name__ == "__main__":
    main()
