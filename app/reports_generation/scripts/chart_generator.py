import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame

from scripts.utils import validate_file_exists, validate_str_is_not_blank, validate_is_number, get_app_specific_actions


def __normalize_file_name(s) -> str:
    s = s.lower()
    # Remove all non-word characters (everything except numbers, letters and '-')
    s = re.sub(r"[^\w\s-]", '', s)
    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", '_', s)

    return s


def __resolve_and_expand_user_path(path: Path) -> Path:
    return path.resolve().expanduser()


def __read_file_as_data_frame(file_path: Path, index_col: str) -> DataFrame:
    if not file_path.exists():
        raise SystemExit(f"File {file_path} does not exist")
    return pd.read_csv(file_path, index_col=index_col)


def __generate_image_name(title: str) -> Path:
    return Path(f"{__normalize_file_name(title)}.png")


def validate_config(config: dict):
    validate_str_is_not_blank(config, "aggregated_csv_path")
    validate_str_is_not_blank(config, "index_col")
    validate_str_is_not_blank(config, "title")
    validate_is_number(config, "image_height_px")
    validate_is_number(config, "image_width_px")


def make_chart(config: dict, results_dir: Path, scenario_status: str) -> Path:
    csv_path_str = config["aggregated_csv_path"]
    index_col = config["index_col"]
    title = config["title"] + f" | Scenario status: {scenario_status}"
    image_height_px = config["image_height_px"]
    image_width_px = config["image_width_px"]

    image_height = image_height_px / 100
    image_width = image_width_px / 100

    file_path = __resolve_and_expand_user_path(Path(csv_path_str))
    data_frame = __read_file_as_data_frame(file_path, index_col)
    print(f"Input data file {file_path} successfully read")

    # Set app-specific mark
    app_specific_actions_list = get_app_specific_actions(file_path)
    for action in app_specific_actions_list:
        data_frame = data_frame.rename(index={action: f"\u2714{action}"})

    data_frame = data_frame.sort_index()
    data_frame.plot.barh(figsize=(image_width, image_height))
    plt.xlabel('Time, ms')
    plt.title(title)
    plt.tight_layout()

    image_path = results_dir / __generate_image_name(Path(csv_path_str).stem)
    plt.savefig(image_path)
    validate_file_exists(image_path, f"Result file {image_path} is not created")
    print(f"Chart file: {image_path.absolute()} successfully created")

    return image_path


def perform_chart_creation(config: dict, results_dir: Path, scenario_status: str) -> Path:
    validate_config(config)
    output_file_path = make_chart(config, results_dir, scenario_status)
    return output_file_path
