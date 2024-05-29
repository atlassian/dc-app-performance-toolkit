from pathlib import Path
from typing import List

from scripts.utils import validate_file_exists, resolve_relative_path, validate_config

SUPPORTED_TEST_ATLASSIAN_PRODUCTS = ("bamboo", "bitbucket", "confluence", "crowd", "jira", "jsm", )
SUMMARY_FILE_NAME = "results_summary.log"
DELIMITER = ('\n================================================================================'
             '========================================\n')


def __get_summary_files(config: dict) -> List[Path]:
    summary_files = []
    for run in config['runs']:
        file_path = resolve_relative_path(run['relativePath']) / SUMMARY_FILE_NAME
        validate_file_exists(file_path, f"File {file_path} does not exists")
        summary_files.append(resolve_relative_path(run['relativePath']) / SUMMARY_FILE_NAME)
    return summary_files


def __get_product_name(config):
    summary_files = __get_summary_files(config)
    for file in summary_files:
        with file.open('r') as f:
            for line in f:
                if "Application" in line:
                    file_content = line
                    for product in SUPPORTED_TEST_ATLASSIAN_PRODUCTS:
                        if product in file_content:
                            return product
                    print("WARNING: No product name found in log files.")


def __get_run_names(config: dict) -> list:
    run_names = []
    for run in config['runs']:
        run_names.append(run['runName'])
    return run_names


def __write_to_summary_report(file_names: List[Path], run_names: List, status: str, output_filename: Path):
    with output_filename.open('a') as outfile:
        outfile.write(f"Scenario status: {status}")
        outfile.write(DELIMITER)
        for file, run_name in zip(file_names, run_names):
            with file.open('r') as infile:
                outfile.write(f"Run name: {run_name}\n\n")
                outfile.write(infile.read())
                outfile.write(DELIMITER)


def __get_output_file_path(config, results_dir) -> Path:
    return results_dir / f"{config['profile']}_summary.log"


def __get_overall_status(files: List[Path]) -> bool:
    for file in files:
        with file.open('r') as f:
            first_line = f.readline()
            if 'FAIL' in first_line:
                return False
    return True


def aggregate(config: dict, results_dir: Path) -> (Path, str):
    validate_config(config)
    output_file_path = __get_output_file_path(config, results_dir)
    summary_files = __get_summary_files(config)
    run_names = __get_run_names(config)
    status_message = 'OK' if __get_overall_status(summary_files) else "FAIL"
    __write_to_summary_report(summary_files, run_names, status_message, output_file_path)
    validate_file_exists(output_file_path, f"Results file {output_file_path} is not created")
    print(f'Results file {output_file_path.absolute()} is created')
    return output_file_path, status_message
