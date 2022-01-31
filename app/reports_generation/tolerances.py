import glob
from pathlib import Path
import os
import warnings

from constants import DEFAULT_TOLERANCE, SUPPORTED_TEST_ATLASSIAN_PRODUCTS
from scripts.utils import read_yaml


class ActionTolerance(dict):
    def __init__(self, tolerances_file_location, tolerance_application_group):
        tolerances = read_yaml(tolerances_file_location)
        tolerances = tolerances.get(tolerance_application_group)
        if not tolerances:
            warnings.warn(f"There are no tolerances for tolerance application group "
                          f"{tolerance_application_group}."
                          f"Using default {0.05} for judgement calculation")
            tolerances = {}

        super(ActionTolerance, self).__init__(tolerances)

    def get_tolerance_range(self, action):
        tolerance = self.get(action)
        if not tolerance:
            warnings.warn(f"There is no tolerance for action {action}. "
                          f"Using default {0.05} for judgement calculation")
            return DEFAULT_TOLERANCE
        return tolerance

    def set_tolerance_range(self, action, tolerance):
        setattr(self, action, tolerance)


def get_tolerances(result_dir):
    result_dir_content = os.path.join(result_dir, '*.yml')
    application_name = next((Path(path).stem for path in glob.glob(result_dir_content)
                             if Path(path).stem in SUPPORTED_TEST_ATLASSIAN_PRODUCTS))
    if not application_name:
        raise Exception(f"Application {application_name} is not in supported list")
    application_action_tolerances = ActionTolerance(tolerances_file_location=__get_tolerance_file(),
                                                    tolerance_application_group=application_name)
    return application_action_tolerances


def __get_tolerance_file():
    # TODO: make it configurable to enable custom tolerances for vendors
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "tolerances.yml")
