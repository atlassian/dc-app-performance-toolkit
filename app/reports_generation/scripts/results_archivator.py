from pathlib import Path
from shutil import make_archive
import yaml

from scripts.utils import validate_config, clean_str, resolve_relative_path


def __zip_folder(folder_path: Path, destination_path: Path) -> Path:
    yml_files = list(folder_path.glob("*.yml"))
    if len(yml_files) > 0:
        __hide_sensitive_info(yml_files)
    archive_path = make_archive(destination_path, 'zip', folder_path)
    return Path(archive_path)


def __hide_sensitive_info(files: list[Path]) -> None:
    for file in files:
        with file.open('r') as f:
            data = yaml.safe_load(f)
        file_edited = False
        if "settings" not in data or "env" not in data["settings"]:
            continue
        if "admin_login" in data["settings"]["env"]:
            data["settings"]["env"]["admin_login"] = "****"
            file_edited = True
        if "admin_password" in data["settings"]["env"]:
            data["settings"]["env"]["admin_password"] = "****"
            file_edited = True
        if file_edited:
            with file.open('w') as f:
                yaml.safe_dump(data, f)


def archive_results(config: dict, results_dir: Path):
    validate_config(config)
    for run in config['runs']:
        results_folder_path = resolve_relative_path(run['relativePath'])
        destination_name = f"{config['profile']}_run_{clean_str(run['runName'])}_{results_folder_path.name}"
        destination_path = results_dir / destination_name
        archive_path = __zip_folder(results_folder_path, destination_path)
        print(f'Folder {results_folder_path} is zipped to {archive_path}')
