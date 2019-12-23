from sys import version_info

SUPPORTED_PYTHON_VERSION = (3, 6)

python_version = version_info[0:2]
if python_version < SUPPORTED_PYTHON_VERSION:
    raise Exception(
        "Python version {} is not supported. "
        "Please use Python version {} or higher.".format(python_version, SUPPORTED_PYTHON_VERSION))
