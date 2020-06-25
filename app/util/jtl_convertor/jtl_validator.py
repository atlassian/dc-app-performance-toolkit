import time
from csv import DictReader
from pathlib import Path
from types import FunctionType
from typing import List, Dict

from util.jtl_convertor.validation_exception import ValidationException
from util.jtl_convertor.validation_funcs import is_not_none, is_number, is_not_blank

CONNECT = 'Connect'
HOSTNAME = 'Hostname'
LATENCY = 'Latency'
ALL_THREADS = 'allThreads'
GRP_THREADS = 'grpThreads'
BYTES = 'bytes'
SUCCESS = 'success'
THREAD_NAME = 'threadName'
RESPONSE_MESSAGE = 'responseMessage'
RESPONSE_CODE = 'responseCode'
LABEL = 'label'
ELAPSED = 'elapsed'
TIME_STAMP = 'timeStamp'
METHOD = 'method'

SUPPORTED_JTL_HEADER: List[str] = [TIME_STAMP, ELAPSED, LABEL, SUCCESS]

VALIDATION_FUNCS_BY_COLUMN: Dict[str, List[FunctionType]] = {
    TIME_STAMP: [is_not_none, is_number],
    ELAPSED: [is_not_none, is_number],
    LABEL: [is_not_blank],
    RESPONSE_CODE: [],
    RESPONSE_MESSAGE: [],
    THREAD_NAME: [],
    SUCCESS: [],
    BYTES: [is_not_none, is_number],
    GRP_THREADS: [is_not_none, is_number],
    ALL_THREADS: [is_not_none, is_number],
    LATENCY: [],
    HOSTNAME: [],
    CONNECT: [],
    METHOD: [],
}


def get_validation_func(column: str) -> List[FunctionType]:
    validation_funcs = VALIDATION_FUNCS_BY_COLUMN.get(column)
    if validation_funcs is None:
        raise Exception(f"There is no validation function for column: [{column}]")

    return validation_funcs


def __validate_value(column: str, value: str) -> None:
    validation_funcs = get_validation_func(column)
    try:
        for validation_func in validation_funcs:
            validation_func(value)
    except ValidationException as e:
        raise ValidationException(f"Column: [{column}]. Validation message: {str(e)}")


def __validate_row(jtl_row: Dict) -> None:
    for column, value in jtl_row.items():
        __validate_value(column, str(value))


def __validate_header(headers: List) -> None:
    for header in SUPPORTED_JTL_HEADER:
        if header not in headers:
            __raise_validation_error(f"Headers is not correct. Required headers is {SUPPORTED_JTL_HEADER}. "
                                     f"{header} is missed")


def __raise_validation_error(error_msg: str) -> None:
    raise ValidationException(error_msg)


def __validate_rows(reader) -> None:
    for file_row_num, jtl_row in enumerate(reader, 2):
        try:
            __validate_row(jtl_row)
        except ValidationException as e:
            __raise_validation_error(f"File row number: {file_row_num}. {str(e)}")


def validate(file_path: Path) -> None:
    print(f'Started validating jtl file: {file_path}')
    start_time = time.time()
    try:
        with file_path.open(mode='r') as f:
            reader: DictReader = DictReader(f)
            __validate_header(reader.fieldnames)
            __validate_rows(reader)

    except (ValidationException, FileNotFoundError) as e:
        raise SystemExit(f"ERROR: Validation failed. File path: [{file_path}]. Validation details: {str(e)}")

    print(f'File: {file_path} validated in {time.time() - start_time} seconds')
