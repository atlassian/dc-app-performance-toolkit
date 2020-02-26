import os
import datetime
from pathlib import Path
import time
import sys
import json
import inspect

JTL_HEADER = "timeStamp,elapsed,label,responseCode,responseMessage,threadName,success,bytes,grpThreads,allThreads," \
             "Latency,Hostname,Connect\n"

def pytest_addoption(parser):
    parser.addoption('--repeat', action='store',
                     help='Number of times to repeat each test')



def __get_current_results_dir():
    if 'TAURUS_ARTIFACTS_DIR' in os.environ:
        return os.environ.get('TAURUS_ARTIFACTS_DIR')
    else:
        # TODO we have error here if 'results' dir does not exist
        results_dir_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        #  pytest_run_results = f'../results/{results_dir_name}_local'
        pytest_run_results = f'results/{results_dir_name}_local'
        os.mkdir(pytest_run_results)
        return pytest_run_results  # in case you just run pytest


# create selenium output files
current_results_dir = __get_current_results_dir()
pytest_results_file = Path(current_results_dir + '/pytests_run.jtl')
pytest_error_file = Path(current_results_dir + '/pytests_run.err')
w3c_timings_pytest_file = Path(current_results_dir + '/w3c_timings_pytests.txt')
print("wc3_timing_pytest_file:" + current_results_dir +  '/w3c_timings_pytests.txt')


if not pytest_results_file.exists():
    with open(pytest_results_file, "w") as file:
        file.write(JTL_HEADER)
    with open(w3c_timings_pytest_file, 'w'):
        pass

#    print(method.__module__)
#   print(method.__qualname__)

def print_timing(func):
    def wrapper(self , session):
        start = time.time()
        error_msg = 'Success'
        full_exception = ''
        interaction = func.__qualname__
        try:
            func(self, session)
            success = True
        except Exception:
            success = False
            # https://docs.python.org/2/library/sys.html#sys.exc_info
            exc_type, full_exception = sys.exc_info()[:2]
            error_msg = exc_type.__name__
        end = time.time()
        timing = str(int((end - start) * 1000))

        with open(pytest_results_file, "a+") as file:
            timestamp = round(time.time() * 1000)
            file.write(f"{timestamp},{timing},{interaction},,{error_msg},,{success},0,0,0,0,,0\n")

        print(f"{timestamp},{timing},{interaction},{error_msg},{success}")

        w3c_timing = 0
        with open(w3c_timings_pytest_file, "a+") as file:
            file.write(f"{{\"timestamp\": {timestamp}, \"timing\": {timing}, \"interation\": \"{interaction}\", "
                       f"\"error\": \"{error_msg}\", \"success\": \"{success}\", \"w3c_timing\": {w3c_timing}}}\n")

        if not success:
            raise Exception(error_msg, full_exception)

    return wrapper

def print_timing_with_create_data(func):
    def wrapper(self , session, create_data):
        start = time.time()
        error_msg = 'Success'
        full_exception = ''
        try:
            func(self, session, create_data)
            success = True
        except Exception:
            success = False
            # https://docs.python.org/2/library/sys.html#sys.exc_info
            exc_type, full_exception = sys.exc_info()[:2]
            error_msg = exc_type.__name__
        end = time.time()
        timing = str(int((end - start) * 1000))

        interaction = func.__qualname__
        with open(pytest_results_file, "a+") as file:
            timestamp = round(time.time() * 1000)
            file.write(f"{timestamp},{timing},{interaction},,{error_msg},,{success},0,0,0,0,,0\n")

        print(f"{timestamp},{timing},{interaction},{error_msg},{success}")

        w3c_timing = 0
        with open(w3c_timings_pytest_file, "a+") as file:
            file.write(f"{{\"timestamp\": {timestamp}, \"timing\": {timing}, \"interation\": \"{interaction}\", "
                       f"\"error\": \"{error_msg}\", \"success\": \"{success}\", \"w3c_timing\": {w3c_timing}}}\n")

        if not success:
            raise Exception(error_msg, full_exception)

    return wrapper