import random
import string
from os import makedirs


def __generate_random_string(length=20):
    return "".join([random.choice(string.ascii_lowercase) for _ in range(length)])


def __write_to_file(file_path, items):
    makedirs(file_path.parent, exist_ok=True)
    with open(file_path, 'w') as f:
        for item in items:
            f.write(f"{item}\n")
