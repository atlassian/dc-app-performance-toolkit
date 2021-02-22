import numbers
from pathlib import Path
from distutils import util
import distutils
import csv


def resolve_path(str_path: str) -> Path:
    return Path(str_path).resolve().expanduser()


def validate_str_is_not_blank(config: dict, key: str):
    value = config.get(key)
    if (value is None) or (not value.strip()):
        raise SystemExit(f"Config [{key}] is not present in config file or its value is empty")
    pass


def validate_is_number(config: dict, key: str):
    value = config.get(key)
    if value is None:
        raise SystemExit(f"Config [{key}] is not present in config file or its value is empty")

    if not isinstance(value, numbers.Number):
        raise SystemExit(f"Value [{value}] is not a number")


def validate_file_exists(file: Path, msg: str):
    if not file.exists():
        raise SystemExit(msg)


def read_csv_by_line(file: Path) -> list:
    lines = []
    with open(file, 'r') as data:
        for line in csv.DictReader(data):
            lines.append(line)
    return lines


def get_app_specific_actions(file: Path) -> list:
    app_specific_list = []
    actions = read_csv_by_line(file)
    for action in actions:
        if bool(distutils.util.strtobool(action['App-specific'])):
            app_specific_list.append(action['Action'])
    return app_specific_list


def validate_config(config: dict):
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


def clean_str(string: str):
    # Return alphanumeric characters from a string
    return ''.join(e for e in string if e.isalnum())
