import sys
from pathlib import Path

import yaml


def get_config() -> dict:
    config_path = resolve_file_path(__get_config_file())
    config = __read_config_file(config_path)
    config['profile'] = config_path.stem
    return config


def __get_config_file() -> str:
    config_file = ''.join(sys.argv[1:])
    if not len(config_file) > 0:
        raise SystemExit("Please provide configuration file path as input parameter")

    return config_file


def __read_config_file(config_file_path: Path) -> dict:
    if not config_file_path.exists():
        raise SystemExit(f"File {config_file_path} does not exist")

    with config_file_path.open(mode="r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise SystemExit(exc, f"Error while parsing configuration file: {config_file_path}")


def resolve_file_path(path: str):
    resolved_file_path = __resolve_and_expand_user_path(Path(path))
    return resolved_file_path


def __resolve_and_expand_user_path(path: Path) -> Path:
    return path.resolve().expanduser()


def get_chart_generator_config(config: dict, agg_csv_path: Path) -> dict:
    config["aggregated_csv_path"] = str(agg_csv_path)
    return config
