from pyad.adcontainer import ADContainer
from pyad.aduser import ADUser
from pyad.adgroup import ADGroup
from pyad.adbase import set_defaults
import string
import random
from pyad.adobject import ADObject
from pyad import addomain

LDAP_SERVER = "10.117.2.135"
LDAP_ADMIN_USERNAME = "INSTENV\Administrator"
LDAP_ADMIN_PASSWORD = "P[dsWEDfJC4Bt=8Vf4cCsM2e"

NUMBER_USERS_TO_CREATE = 10
DEFAULT_USER_PASSWORD = "Password123"
AD_GROUP_USER_DISTRIBUTION = {'jira-software-user': 80, 'jira-administrators': 20}


def generate_string(length):
    return "".join([random.choice(string.ascii_letters + ' ') for _ in range(length)]).replace(" ", "").capitalize()


def generate_usernames(user_count=1):
    users_list = []
    for user in range(user_count):
        users_list.append(f"{generate_string(5)} {generate_string(5)}")
    return users_list


set_defaults(ldap_server=LDAP_SERVER, username=LDAP_ADMIN_USERNAME, password=LDAP_ADMIN_PASSWORD)
ou = ADContainer.from_dn("ou=TestUsers, dc=smoroz6,dc=local")
jira_software_users_group = ADGroup.from_dn("CN=jira-software-users,OU=TestGroups,DC=smoroz6,DC=local")
jira_administrators_group = ADGroup.from_dn("CN=jira-administrators,OU=TestGroups,DC=smoroz6,DC=local")
AD_GROUP_USER_DISTRIBUTION_PERC = {jira_software_users_group: 80, jira_administrators_group: 20}
AD_GROUP_USER_DISTRIBUTION_COUNT = {jira_software_users_group: int(
    (AD_GROUP_USER_DISTRIBUTION_PERC[jira_software_users_group] * NUMBER_USERS_TO_CREATE) / 100) or 1,
                                    jira_administrators_group: int((AD_GROUP_USER_DISTRIBUTION_PERC[
                                                                        jira_administrators_group] * NUMBER_USERS_TO_CREATE) / 100) or 1}
print(AD_GROUP_USER_DISTRIBUTION_COUNT)


def divide_users_by_batch(users, dict):
    batches_n = len(dict.keys())
    print(f'batches: {batches_n}')
    final_dict = {}
    start_batch = 0
    for i in range(batches_n):
        batch = users[start_batch: start_batch + dict[list(dict.keys())[i]]]
        start_batch = start_batch + dict[list(dict.keys())[i]]
        final_dict[list(dict.keys())[i]] = batch
    return final_dict


if __name__ == "__main__":
    users_to_create = generate_usernames(NUMBER_USERS_TO_CREATE)
    counter = 0
    # Create users into groups
    users_groups_dict = divide_users_by_batch(users=users_to_create, dict=AD_GROUP_USER_DISTRIBUTION_COUNT)
    created_users = []
    for group, users in users_groups_dict.items():
        for user in users:
            new_user = ADUser.create(user, ou, password=DEFAULT_USER_PASSWORD)
            new_user.add_to_group(group)
            created_users.append(user)
            print(f'Users {new_user} was added to group: {group}')
    print(f'Users with groups created {len(created_users)}')

    # Create other users WITHOUT groups:
    for user in users_to_create:
        if user not in created_users:
            new_user = ADUser.create(user, ou, password=DEFAULT_USER_PASSWORD)







