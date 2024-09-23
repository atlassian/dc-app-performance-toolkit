from pathlib import Path
from shutil import make_archive

from scripts.utils import validate_config, clean_str, resolve_relative_path


def __zip_folder(folder_path: Path, destination_path: Path) -> Path:
    archive_path = make_archive(destination_path, 'zip', folder_path)
    return Path(archive_path)


def archive_results(config: dict, results_dir: Path):
    validate_config(config)
    for run in config['runs']:
        results_folder_path = resolve_relative_path(run['relativePath'])
        destination_name = f"{config['profile']}_run_{clean_str(run['runName'])}_{results_folder_path.name}"
        destination_path = results_dir / destination_name
        archive_path = __zip_folder(results_folder_path, destination_path)
        print(f'Folder {results_folder_path} is zipped to {archive_path}')
