import sys
from pathlib import Path

import yaml

from util.data_preparation.confluence.api import ApiConfluence


def __get_app_dir():
    return Path(__file__).parents[3]


def get_perf_users_count():
    with open(__get_app_dir() / "confluence.yml", 'r') as file:
        jira_yaml = yaml.load(file, Loader=yaml.FullLoader)
        users_count = jira_yaml['settings']['env']['concurrency']
        return users_count


def write_test_data_to_files(dataset):
    # TODO extract paths to project_paths
    file_path = Path(__file__).parents[3] / "datasets" / "confluence"

    def write_to_file(file_name, list):
        with open(file_path / file_name, 'w') as f:
            for item in list:
                f.write("{}\n".format(item))

    pages = [f"{page['id']},{page['space']['key']}" for page in dataset['pages']]
    write_to_file('pages.csv', pages)

    blogs = [f"{blog['id']},{blog['space']['key']}" for blog in dataset['blogs']]
    write_to_file('blogs.csv', blogs)

    users = [f"{user[0]},{user[1]}" for user in dataset['users']]
    write_to_file('users.csv', users)


def main():
    print("Started preparing data")

    url = sys.argv[1]
    print("Server url: ", url)

    dataset = dict()

    confluence_api = ApiConfluence(url)
    dataset["users"] = confluence_api.create_users("performance", get_perf_users_count())

    confluence_api.base_auth = dataset["users"][0]
    dataset["pages"] = confluence_api.get_content(0, 5000, "page")
    dataset["blogs"] = confluence_api.get_content(0, 500, "blogpost")

    write_test_data_to_files(dataset)


if __name__ == "__main__":
    main()
