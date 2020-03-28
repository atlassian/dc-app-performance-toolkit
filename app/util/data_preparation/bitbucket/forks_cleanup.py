from util.conf import BITBUCKET_SETTINGS
from util.data_preparation.api.bitbucket_clients import BitbucketRestClient
from util.project_paths import BITBUCKET_USERS
import csv

URL = BITBUCKET_SETTINGS.server_url


def read_file(file_path):
    with open(file_path, 'r') as fs:
        reader = csv.reader(fs)
        return list(reader)


def get_users_repos(users, api_client):
    user_repos = []
    for user in users:
        repos = api_client.get_user_repos(user_name=user[1])
        for repo in repos:
            if 'origin' in repo.keys():
                user_repos.append([user[1], repo['slug']])
    return user_repos


def delete_repos(repos, api_client):
    for repo in repos:
        response = api_client.delete_user_repo(username=repo[0], repo_slug=repo[1])
        print(f'{response["message"]} Repository {repo[1]}, user {repo[0]}')


if __name__ == "__main__":
    users = read_file(BITBUCKET_USERS)
    bitbucket_client = BitbucketRestClient(URL, BITBUCKET_SETTINGS.admin_login, BITBUCKET_SETTINGS.admin_password)
    repos_to_delete = get_users_repos(users, api_client=bitbucket_client)
    delete_repos(repos_to_delete, api_client=bitbucket_client)
