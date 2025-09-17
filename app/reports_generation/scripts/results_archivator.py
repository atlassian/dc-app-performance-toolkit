from pathlib import Path
from shutil import make_archive
import re

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
            lines = f.readlines()
        new_lines = []
        file_edited = False
        for line in lines:
            if re.match(r'\s*admin_password\s*:', line):
                line = re.sub(r'(:\s*).+', r'\1****', line)
                file_edited = True
            new_lines.append(line)
        if file_edited:
            with file.open('w') as f:
                f.writelines(new_lines)


def archive_results(config: dict, results_dir: Path):
    validate_config(config)
    for run in config['runs']:
        results_folder_path = resolve_relative_path(run['relativePath'])
        destination_name = f"{config['profile']}_run_{clean_str(run['runName'])}_{results_folder_path.name}"
        destination_path = results_dir / destination_name
        archive_path = __zip_folder(results_folder_path, destination_path)
        print(f'Folder {results_folder_path} is zipped to {archive_path}')
