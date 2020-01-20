from sys import version_info

from util.conf import TOOLKIT_VERSION

MIN_SUPPORTED_PYTHON_VERSION = (3, 6, 0)


print("Data Center App Performance Toolkit version: {}".format(TOOLKIT_VERSION))

python_version = version_info[0:3]
print("Python version: {}".format(python_version))
if python_version < MIN_SUPPORTED_PYTHON_VERSION:
    raise Exception(
        "Python version {} is not supported. "
        "Please use Python version {} or higher.".format(python_version, MIN_SUPPORTED_PYTHON_VERSION))
