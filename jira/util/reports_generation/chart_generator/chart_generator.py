import numbers
import re
import sys
from pathlib import Path
import os

import matplotlib.pyplot as plt
import pandas as pd
import yaml
from pandas import DataFrame


def __normalize_file_name(s) -> str:
    s = s.lower()
    # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"[^\w\s-]", '', s)
    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", '_', s)

    return s


def __resolve_and_expand_user_path(path: Path) -> Path:
    return path.resolve().expanduser()


def __read_file_as_data_frame(file_path: Path, index_col: str) -> DataFrame:
    return pd.read_csv(file_path, index_col=index_col)


def __get_results_dir(csv_path_str: str) -> Path:
    path = Path(csv_path_str).parents[0]
    path.mkdir(parents=True, exist_ok=True)
    return path


def __generate_image_name(title: str) -> Path:
    return Path(f"{__normalize_file_name(title)}.png")


def __get_config_file() -> str:
    config_file = ''.join(sys.argv[1:])
    if not len(config_file) > 0:
        raise SystemExit("Please provide configuration file path as input parameter")

    return config_file


def __validate_is_not_blank(config: dict, key: str):
    value = config.get(key)
    if (value is None) or (not value.strip()):
        raise SystemExit(f"Config [{key}] is not present in config file or its value is empty")
    pass


def __validate_is_number(config: dict, key: str):
    value = config.get(key)
    if value is None:
        raise SystemExit(f"Config [{key}] is not present in config file or its value is empty")

    if not isinstance(value, numbers.Number):
        raise SystemExit(f"Value [{value}] is not a number")


def __validate_file_exists(filename: str):
    if not os.path.exists(filename):
        raise SystemExit(f"Config file [{filename}] does not exist")


def validate_config(config: dict):
    __validate_is_not_blank(config, "aggregated_csv_path")
    __validate_is_not_blank(config, "index_col")
    __validate_is_not_blank(config, "title")
    __validate_is_number(config, "image_height_px")
    __validate_is_number(config, "image_width_px")
    __validate_file_exists(config["aggregated_csv_path"])
    return


def __read_config_file(config_file: str) -> dict:
    resolved_file_path = __resolve_and_expand_user_path(Path(config_file))
    if not resolved_file_path.exists():
        raise SystemExit(f"File {resolved_file_path} does not exist")

    with resolved_file_path.open(mode="r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise SystemExit(exc, f"Error while parsing configuration file: {config_file}")


def make_chart(csv_path_str: str, index_col: str, title: str, image_height_px, image_width_px) -> Path:
    image_height = image_height_px / 100
    image_width = image_width_px / 100

    file_path = __resolve_and_expand_user_path(Path(csv_path_str))
    data_frame = __read_file_as_data_frame(file_path, index_col)
    print(f"Input data file {file_path} successfully read")

    data_frame = data_frame.sort_index()
    data_frame.plot.barh(figsize=(image_width, image_height))
    plt.xlabel('Time, ms')
    plt.title(title)
    plt.tight_layout()

    image_path = __get_results_dir(csv_path_str) / __generate_image_name(Path(csv_path_str).stem)
    plt.savefig(image_path)
    print(f"Chart file: {image_path.absolute()} successfully created")

    return image_path


def perform_chart_creation(config_file_path: str) -> Path:
    config = __read_config_file(config_file_path)
    print(f"Config: {config_file_path} successfully read")

    validate_config(config)

    print(f"Config: {config_file_path} successfully validated")

    return make_chart(config["aggregated_csv_path"], config["index_col"], config["title"], config["image_height_px"],
                      config["image_width_px"])


def main():
    config_file = __get_config_file()
    perform_chart_creation(config_file)


if __name__ == "__main__":
    main()
