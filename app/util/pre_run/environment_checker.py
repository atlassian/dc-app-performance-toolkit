from sys import version_info

SUPPORTED_PYTHON_VERSIONS = ["3.8", "3.9", "3.10", "3.11"]

python_full_version = '.'.join(map(str, version_info[0:3]))
python_short_version = '.'.join(map(str, version_info[0:2]))
print("Python version: {}".format(python_full_version))
if python_short_version not in SUPPORTED_PYTHON_VERSIONS:
    raise SystemExit("Python version {} is not supported. "
                     "Supported versions: {}.".format(python_full_version, SUPPORTED_PYTHON_VERSIONS))

# Print toolkit version after Python check
from util.conf import TOOLKIT_VERSION  # noqa E402

print("Data Center App Performance Toolkit version: {}".format(TOOLKIT_VERSION))
