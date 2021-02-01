# -*- encoding: utf-8 -*-

import re
from pathlib import Path
import csv
import tempfile

import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame

from scripts.utils import validate_file_exists, validate_str_is_not_blank, validate_is_number, read_json_file

APPS = ['jira', 'confluence', 'bitbucket', 'jsm']
TEST_TYPES = ['selenium', 'jmeter', 'locust']
DEFAULT_ACTIONS_PATH = '../util/default_test_actions.json'


def __normalize_file_name(s) -> str:
    s = s.lower()
    # Remove all non-word characters (everything except numbers, letters and '-')
    s = re.sub(r"[^\w\s-]", '', s)
    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", '_', s)

    return s


def __resolve_and_expand_user_path(path: Path) -> Path:
    return path.resolve().expanduser()


def __get_all_default_actions():
    full_actions_list = []
    actions_data = read_json_file(DEFAULT_ACTIONS_PATH)
    for app in APPS:
        for test_type in TEST_TYPES:
            for action in actions_data[app][test_type]:
                full_actions_list.append(action)
    return full_actions_list


def __mark_as_app_specific(action_name: str):
    if action_name not in __get_all_default_actions():
        return f'\u2714{action_name}'
    else:
        return action_name


def __read_file_as_data_frame(file_path: Path, index_col: str) -> DataFrame:
    if not file_path.exists():
        raise SystemExit(f"File {file_path} does not exist")

    lines = []
    with open(file_path, 'r') as res_file:
        for line in csv.DictReader(res_file):
            lines.append(line)

    # Mark as app-specific if exists
    for line in lines:
        line['Action'] = __mark_as_app_specific(line['Action'])

    fields = list(lines[0].keys())
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_csv = Path(tmp_dir) / Path(f'tmp_scale_profile.csv')
        with open(tmp_csv, 'w') as tmp_file:
            w = csv.writer(tmp_file)
            w.writerow(fields)
            for line in lines:
                w.writerow(line[field] for field in fields)
        with open(tmp_csv, 'r') as f:
            return pd.read_csv(f, index_col=index_col)


def __generate_image_name(title: str) -> Path:
    return Path(f"{__normalize_file_name(title)}.png")


def validate_config(config: dict):
    validate_str_is_not_blank(config, "aggregated_csv_path")
    validate_str_is_not_blank(config, "index_col")
    validate_str_is_not_blank(config, "title")
    validate_is_number(config, "image_height_px")
    validate_is_number(config, "image_width_px")


def make_chart(config: dict, results_dir: Path) -> Path:
    csv_path_str = config["aggregated_csv_path"]
    index_col = config["index_col"]
    title = config["title"]
    image_height_px = config["image_height_px"]
    image_width_px = config["image_width_px"]

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

    image_path = results_dir / __generate_image_name(Path(csv_path_str).stem)
    plt.savefig(image_path)
    validate_file_exists(image_path, f"Result file {image_path} is not created")
    print(f"Chart file: {image_path.absolute()} successfully created")

    return image_path


def perform_chart_creation(config: dict, results_dir: Path) -> Path:
    validate_config(config)
    output_file_path = make_chart(config, results_dir)
    return output_file_path
