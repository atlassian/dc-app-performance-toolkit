import os
import datetime
from pathlib import Path
import time
import sys
import json
import inspect
import threading
import os
from os import path
global_lock = threading.Lock()
import random

JTL_HEADER = "timeStamp,elapsed,label,responseCode,responseMessage,threadName,success,bytes,grpThreads,allThreads," \
             "Latency,Hostname,Connect\n"
HOSTNAME = os.environ.get('application_hostname')

PRINT_IN_SHELL = os.environ.get('print_in_shell')


def pytest_addoption(parser):
    parser.addoption('--repeat', action='store',
                     help='Number of times to repeat each test')

def print_in_shell(value):
    if PRINT_IN_SHELL=="No":
        pass
    else:
        print(value)


def __get_current_results_dir():
    if 'TAURUS_ARTIFACTS_DIR' in os.environ:
        return os.environ.get('TAURUS_ARTIFACTS_DIR')
    else:
        #   raise SystemExit('Taurus result directory could not be found')
        results_dir_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        #  pytest_run_results = f'../results/{results_dir_name}_local'
        pytest_run_results = f'results/{results_dir_name}_local'
        if os.path.isdir(f'results/'):
            pass
        else:
            os.mkdir(f'results/')
        if os.path.isdir(pytest_run_results):
            print ("Dir exist")
        else:
            os.mkdir(pytest_run_results)
        return pytest_run_results  # in case you just run pytest


# create selenium output files
current_results_dir = __get_current_results_dir()
basepath = path.dirname(__file__)
pytest_results_file = Path(current_results_dir + '/pytests_run.jtl')
pytest_error_file = Path(current_results_dir + '/pytests_run.err')
#w3c_timings_pytest_file = Path(current_results_dir + '/w3c_timings_pytests.txt')
#print("wc3_timing_pytest_file:" + current_results_dir +  '/w3c_timings_pytests.txt')
delete_created_objects_path = path.abspath(path.join(basepath, "deleteCreatedObjects"))

#CURRENT_PATH = pathlib.Path().absolute()
projects_path = path.abspath(path.join(basepath, "projects"))

if not pytest_results_file.exists():
    with open(pytest_results_file, "w") as file:
        file.write(JTL_HEADER)
#    with open(w3c_timings_pytest_file, 'w'):
#        pass

def readProjectCmd():
    result = []
    try:
        with open(projects_path, "r") as fp:
            line = fp.readline()
            while line:
                dict = eval(line)
                result.append(dict)
                line = fp.readline()
    except IOError:
        print("File not accessible read " + 'project')
    return result

projects = readProjectCmd()

def writeLockedCmd(delete_request, type , id):
    global global_lock
    try:
        global_lock.acquire()
        with open(delete_created_objects_path, "a") as f:
            f.write(delete_request)
            f.close()
        global_lock.release()
    except IOError:
        print("Write to deleteCreateObjects file failed" + type +  id)
        global_lock.release()

def saveRemoveDiagramCmd(diagramId):
    diagrams_delete_request ='/rest/dependency-map/1.0/diagram/' + str(diagramId) + '\n'
    writeLockedCmd(diagrams_delete_request, "Diagram" , diagramId)


def saveRemoveIssueLinkCmd(issueLinkId):
    issueLink_delete_request ='/rest/api/latest/issueLink/' + str(issueLinkId) + '\n'
    writeLockedCmd(issueLink_delete_request, "IssuLink" , issueLinkId)

def getRandomFixture(session):
    page = 0
    exit = 0
    projectId = getRandomProjectId()
    print("PROJECT" + str( projectId ))
    while True:
        diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=' + str(page) + '&resultsPerPage=50')
        assert diagrams_response.status_code == 200
        diagrams_response_filters = diagrams_response.json()["filters"]
        print ("all filters json: " + str(diagrams_response_filters))
        page = page + 1

        if len(diagrams_response_filters) ==0:
            break

        for filter in diagrams_response_filters:
            filter_id = str (filter['filterKey'])
            print(filter_id)
            permission_response = session.get('/rest/api/2/filter/' + filter_id + '/permission')
            for sharePer in permission_response.json():
                if sharePer['type']=='project' and sharePer['project']['id'] == projectId   :
                        filterKey=filter_id
                        exit = 1
                        break
            if exit ==1:
                break

        if exit == 1:
            break
    return filterKey

def getRandomProjectId():
    nrProjects = len(projects)
    projectId=projects[random.randint(0,nrProjects-1)]['id']
    return projectId



def print_timing(func):
    def wrapper(self , base_url, session):
        start = time.time()
        error_msg = 'Success'
        full_exception = ''
        interaction = func.__qualname__
        try:
            func(self, base_url, session)
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
    def wrapper(self , base_url, session, create_data):
        start = time.time()
        error_msg = 'Success'
        full_exception = ''
        interaction = func.__qualname__
        try:
            func(self, base_url, session, create_data)
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