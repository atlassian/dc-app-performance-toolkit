import os
import datetime
from pathlib import Path
import time
import sys
import json
import inspect
import threading
global_lock = threading.Lock()

JTL_HEADER = "timeStamp,elapsed,label,responseCode,responseMessage,threadName,success,bytes,grpThreads,allThreads," \
             "Latency,Hostname,Connect\n"
HOSTNAME = os.environ.get('application_hostname')


def pytest_addoption(parser):
    parser.addoption('--repeat', action='store',
                     help='Number of times to repeat each test')



def __get_current_results_dir():
    if 'TAURUS_ARTIFACTS_DIR' in os.environ:
        return os.environ.get('TAURUS_ARTIFACTS_DIR')
    else:
     #   raise SystemExit('Taurus result directory could not be found')
        results_dir_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
       #  pytest_run_results = f'../results/{results_dir_name}_local'
        pytest_run_results = f'results/{results_dir_name}_local'
        if os.path.isdir(pytest_run_results):
            print ("Dir exist")
        else:
            os.mkdir(pytest_run_results)
        return pytest_run_results  # in case you just run pytest


# create selenium output files
current_results_dir = __get_current_results_dir()
pytest_results_file = Path(current_results_dir + '/pytests_run.jtl')
pytest_error_file = Path(current_results_dir + '/pytests_run.err')
#w3c_timings_pytest_file = Path(current_results_dir + '/w3c_timings_pytests.txt')
#print("wc3_timing_pytest_file:" + current_results_dir +  '/w3c_timings_pytests.txt')
out_file_path = Path(current_results_dir + '/deleteCreatedObjects')


if not pytest_results_file.exists():
    with open(pytest_results_file, "w") as file:
        file.write(JTL_HEADER)
#    with open(w3c_timings_pytest_file, 'w'):
#        pass

def saveRemoveDiagramCmd(diagramId):
    try:
        global_lock.acquire()
        with open(out_file_path, "a") as f:
            diagrams_delete_request ='http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram/' + str(diagramId)
            f.write(diagrams_delete_request)
            f.write("\n")
            f.close()
        global_lock.release()
    except IOError:
        print("File not accessible" + diagramId)

def saveRemoveIssueLinkCmd(issueLinkId):
    try:
        global_lock.acquire()
        with open(out_file_path, "a") as f:
            issueLink_delete_request ='http://'  + HOSTNAME + ':8080/rest/api/latest/issueLink/' + str(issueLinkId)
            f.write(issueLink_delete_request)
            f.write("\n")
            f.close()
        global_lock.release()
    except IOError:
        print("File not accessible" + issueLinkId)


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
        timestamp = round(time.time() * 1000)

        global_lock.acquire()
        with open(pytest_results_file, "a") as file:
            file.write(f"{timestamp},{timing},{interaction},,{error_msg},,{success},0,0,0,0,,0\n")
        global_lock.release()

        print(f"{timestamp},{timing},{interaction},{error_msg},{success}")

        if not success:
            raise Exception(error_msg, full_exception)

    return wrapper

def print_timing_with_additional_arg(func):
    def wrapper(self , session, create_data):
        start = time.time()
        error_msg = 'Success'
        full_exception = ''
        interaction = func.__qualname__
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


        timestamp = round(time.time() * 1000)

        global_lock.acquire()
        with open(pytest_results_file, "a") as file:
            file.write(f"{timestamp},{timing},{interaction},,{error_msg},,{success},0,0,0,0,,0\n")
        global_lock.release()

        print(f"{timestamp},{timing},{interaction},{error_msg},{success}")

        if not success:
            raise Exception(error_msg, full_exception)

    return wrapper