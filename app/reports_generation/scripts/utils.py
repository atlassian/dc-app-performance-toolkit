import csv
import numbers
from pathlib import Path


def resolve_relative_path(str_path: str) -> Path:
    """
    Resolve relative path  from .yml scenario configuration file.
    Expected working dir for csv_chart_generator.py: ./dc-app-performance-toolkit/app/reports_generation
    Expected relative path starting from ./dc-app-performance-toolkit folder.
    """
    expected_working_dir_name = 'reports_generation'
    working_dir = Path().resolve().expanduser()
    if working_dir.name != expected_working_dir_name:
        raise SystemExit(f"ERROR: expected working dir name: {expected_working_dir_name}, actual: {working_dir.name}")
    return Path().resolve().expanduser().parents[1] / str_path


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


def string_to_bool(val):
    """
    Convert a string representation of truth to a boolean.
    True values are 'y', 'yes', 't', 'true', 'on', and '1';
    False values are 'n', 'no', 'f', 'false', 'off', and '0'.
    Raises ValueError if 'val' is anything else.
    """
    val = val.strip().lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError(f"Invalid truth value: {val}")


def get_app_specific_actions(file: Path) -> list:
    app_specific_list = []
    actions = read_csv_by_line(file)
    for action in actions:
        if string_to_bool(action['App-specific']):
            app_specific_list.append(action['Action'])
    return app_specific_list


def validate_config(config: dict):
    validate_str_is_not_blank(config, 'column_name')
    validate_str_is_not_blank(config, 'profile')

    runs = config.get('runs')
    if not isinstance(runs, list):
        raise SystemExit('Config key "runs" should be a list')

    for run in runs:
        if not isinstance(run, dict):
            raise SystemExit('Config key "run" should be a dictionary')

        validate_str_is_not_blank(run, 'runName')
        validate_str_is_not_blank(run, 'relativePath')


def clean_str(string: str):
    # replace spaces with "_"
    string = string.replace(" ", "_")
    # Return alphanumeric characters from a string, except "_"
    return ''.join(e for e in string if e.isalnum() or e == "_")
