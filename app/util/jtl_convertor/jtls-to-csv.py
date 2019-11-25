import os
import sys
import tempfile
import time
from pathlib import Path
from typing import IO, List, Set

from util.jtl_convertor import jtl_validator

RESULTS_CSV_NAME = 'results.csv'
ENV_JMETER_VERSION = 'JMETER_VERSION'
ENV_TAURUS_ARTIFACT_DIR = 'TAURUS_ARTIFACTS_DIR'
TEMPLATE_PLUGIN_COMMAND = 'java -Djava.awt.headless=true -jar {libs_home}cmdrunner-2.2.jar ' \
                          '--tool Reporter ' \
                          '--tool Reporter --generate-csv {output_csv} ' \
                          '--input-jtl "{input_jtl}" ' \
                          '--plugin-type AggregateReport'
CSV_HEADER = 'Label,# Samples,Average,Median,90% Line,95% Line,99% Line,' \
             'Min,Max,Error %,Throughput,Received KB/sec,Std. Dev.\n'


def __count_file_lines(stream: IO) -> int:
    return sum(1 for _ in stream)


def __reset_file_stream(stream: IO) -> None:
    stream.seek(0)


def __convert_jtl_to_csv(input_file_path: Path, output_file_path: Path, jmeter_libs_home: Path) -> None:
    if not input_file_path.exists():
        raise SystemExit(f'Input file {output_file_path} does not exist')

    command = TEMPLATE_PLUGIN_COMMAND.format(libs_home=str(jmeter_libs_home) + os.path.sep,
                                             output_csv=output_file_path,
                                             input_jtl=input_file_path)
    print(os.popen(command).read())
    if not output_file_path.exists():
        raise SystemExit(f'Something went wrong. Output file {output_file_path} does not exist')

    print(f'Created file {output_file_path}')


def __get_jmeter_home() -> Path:
    jmeter_version = os.getenv(ENV_JMETER_VERSION)
    if jmeter_version is None:
        raise SystemExit(f'Error: env variable {ENV_JMETER_VERSION} is not set')

    return Path().home() / '.bzt' / 'jmeter-taurus' / jmeter_version


def __get_jmeter_lib_dir() -> Path:
    return __get_jmeter_home() / 'lib'


def __change_file_extension(file_name: str, new_extension) -> str:
    return __get_file_name_without_extension(file_name) + new_extension


def __get_file_name_without_extension(file_name):
    return os.path.splitext(file_name)[0]


def __read_csv_without_first_and_last_line(results_file_stream, input_csv):
    with input_csv.open(mode='r') as file_stream:
        lines_number: int = __count_file_lines(file_stream)
        __reset_file_stream(file_stream)

        for cnt, line in enumerate(file_stream, 1):
            if cnt != 1 and cnt != lines_number:
                results_file_stream.write(line)
    print(f'File {input_csv} successfully read')


def __create_results_csv(csv_list: List[Path], results_file_path: Path) -> None:
    with results_file_path.open(mode='w') as results_file_stream:
        results_file_stream.write(CSV_HEADER)

        for temp_csv_path in csv_list:
            __read_csv_without_first_and_last_line(results_file_stream, temp_csv_path)

    if not results_file_path.exists():
        raise SystemExit(f'Something went wrong. Output file {results_file_path} does not exist')
    print(f'Created file {results_file_path}')


def __validate_file_names(file_names: List[str]):
    file_names_set: Set[str] = set()

    for file_name in file_names:
        if '.' not in file_name:
            raise SystemExit(f'File name {file_name} does not have extension')

        file_name_without_extension = __get_file_name_without_extension(file_name)
        if file_name_without_extension in file_names_set:
            raise SystemExit(f'Duplicated file name {file_name_without_extension}')

        file_names_set.add(file_name_without_extension)


def main():
    file_names = sys.argv[1:]
    __validate_file_names(file_names)
    artifacts_dir: str = os.getenv(ENV_TAURUS_ARTIFACT_DIR)
    if artifacts_dir is None:
        raise SystemExit(f'Error: env variable {ENV_TAURUS_ARTIFACT_DIR} is not set')

    artifacts_dir_path = Path(artifacts_dir)
    with tempfile.TemporaryDirectory() as tmp_dir:
        jmeter_lib_dir = __get_jmeter_lib_dir()
        temp_csv_list: List[Path] = []
        for file_name in file_names:
            jtl_file_path = artifacts_dir_path / file_name
            jtl_validator.validate(jtl_file_path)
            csv_file_path = Path(tmp_dir) / __change_file_extension(file_name, '.csv')
            __convert_jtl_to_csv(jtl_file_path, csv_file_path, jmeter_lib_dir)
            temp_csv_list.append(csv_file_path)

        results_file_path = artifacts_dir_path / RESULTS_CSV_NAME
        __create_results_csv(temp_csv_list, results_file_path)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f'Done in {time.time() - start_time} seconds')
