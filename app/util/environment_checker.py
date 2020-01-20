from sys import version_info

from util.conf import TOOLKIT_VERSION

SUPPORTED_PYTHON_VERSION = (3, 6)


print("Data Center App Performance Toolkit version: {}".format(TOOLKIT_VERSION))

python_version = version_info[0:2]
if python_version < SUPPORTED_PYTHON_VERSION:
    raise Exception(
        "Python version {} is not supported. "
        "Please use Python version {} or higher.".format(python_version, SUPPORTED_PYTHON_VERSION))
