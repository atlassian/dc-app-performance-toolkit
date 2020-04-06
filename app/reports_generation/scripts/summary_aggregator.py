from pathlib import Path
from typing import List

from scripts.utils import validate_str_is_not_blank, validate_file_exists, resolve_path

SUMMARY_FILE_NAME = "results_summary.log"
DELIMITER = ('\n================================================================================'
             '========================================\n')


def __validate_config(config: dict):
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


def __get_summary_files(config: dict) -> List[Path]:
    summary_files = []
    for run in config['runs']:
        file_path = resolve_path(run['fullPath']) / SUMMARY_FILE_NAME
        validate_file_exists(file_path, f"File {file_path} does not exists")
        summary_files.append(resolve_path(run['fullPath']) / SUMMARY_FILE_NAME)
    return summary_files


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


def aggregate(config: dict, results_dir: Path) -> Path:
    __validate_config(config)
    output_file_path = __get_output_file_path(config, results_dir)
    summary_files = __get_summary_files(config)
    run_names = __get_run_names(config)
    status_message = 'OK' if __get_overall_status(summary_files) else "FAIL"
    __write_to_summary_report(summary_files, run_names, status_message, output_file_path)
    validate_file_exists(output_file_path, f"Results file {output_file_path} is not created")
    print(f'Results file {output_file_path.absolute()} is created')
    return output_file_path
