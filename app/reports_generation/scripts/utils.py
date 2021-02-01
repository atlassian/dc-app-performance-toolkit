import numbers
from pathlib import Path
import json

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


def read_json_file(file_path):
    with open(file_path) as json_file:
        data = json.load(json_file)
        return data
