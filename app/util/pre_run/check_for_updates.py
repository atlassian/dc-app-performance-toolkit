from util.common_util import get_latest_version, get_current_version, get_unsupported_version

latest_version = get_latest_version()
current_version = get_current_version()
unsupported_version = get_unsupported_version()

if latest_version is None:
    print('Warning: failed to get the latest version')
elif unsupported_version is None:
    print('Warning: failed to get the unsupported version')
elif current_version <= unsupported_version:
    raise SystemExit(f"DCAPT version {current_version} is no longer supported. "
                     f"Consider an upgrade to the latest version: {latest_version}")
elif current_version < latest_version:
    print(f"Warning: DCAPT version {current_version} is outdated. "
          f"Consider upgrade to the latest version: {latest_version}.")
elif current_version == latest_version:
    print(f"Info: DCAPT version {current_version} is the latest.")
else:
    print(f"Info: DCAPT version {current_version} "
          f"is ahead of the latest production version: {latest_version}.")
