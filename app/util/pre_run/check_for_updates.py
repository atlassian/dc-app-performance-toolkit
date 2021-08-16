from util.common_util import latest_version, current_version, unsupported_version

if latest_version() is None:
    print('Please check your connection to the internet')
elif current_version() <= unsupported_version():
    raise SystemExit(f"DCAPT version {current_version()} is no longer supported. "
                     f"Consider an upgrade to the latest version: {latest_version()}")
elif current_version() < latest_version():
    print(f"Warning: DCAPT version {current_version()} is outdated. "
          f"Consider upgrade to the latest version: {latest_version()}.")
elif current_version() == latest_version():
    print(f"Info: DCAPT version {current_version()} is latest.")
else:
    print(f"Info: DCAPT version {current_version()} "
          f"is ahead of the latest production version: {latest_version()}.")
