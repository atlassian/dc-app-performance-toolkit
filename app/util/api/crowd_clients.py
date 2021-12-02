from util.api.abstract_clients import RestClient, LOGIN_POST_HEADERS


BATCH_SIZE_USERS = 1000


class CrowdRestClient(RestClient):

    def add_user(self,
                 name: str,
                 password: str,
                 first_name: str,
                 last_name: str,
                 display_name: str = None,
                 email: str = None,
                 active: bool = True):
        api_url = self.host + "/rest/usermanagement/1/user"
        payload = {
            "name": name,
            "password": {"value": password},
            "active": active,
            "first-name": first_name,
            "last-name": last_name,
            "display-name": display_name or f"{first_name} {last_name}",
            "email": email or name + '@localdomain.com'
        }

        response = self.post(api_url, "Could not create crowd user", body=payload)

        return response.json()

    def search(self, entity_type: str = "user", start_index: int = 0, max_results: int = 1000, restriction: str = '',
               expand: str = 'user'):
        api_url = self.host + f"/rest/usermanagement/1/search" \
                              f"?entity-type={entity_type}" \
                              f"&start-index={start_index}&max-results={max_results}&restriction={restriction}" \
                              f"&expand={expand}"
        response = self.get(api_url, "Search failed")

        return [i['name'] for i in response.json()[f'{entity_type}s']]

    def users_search_parallel(self, cql: str = '', max_results: int = 1000):
        """
        Parallel version
        """
        from multiprocessing import cpu_count
        from multiprocessing.pool import ThreadPool
        print("Users parallel search")

        if max_results % BATCH_SIZE_USERS == 0:
            loop_count = max_results // BATCH_SIZE_USERS
            last_BATCH_SIZE_USERS = BATCH_SIZE_USERS
        else:
            loop_count = max_results // BATCH_SIZE_USERS + 1
            last_BATCH_SIZE_USERS = max_results % BATCH_SIZE_USERS

        def search_users(i):
            nonlocal loop_count, last_BATCH_SIZE_USERS
            if i == loop_count - 1:
                loop_max_results = last_BATCH_SIZE_USERS
            else:
                loop_max_results = BATCH_SIZE_USERS

            start_index = BATCH_SIZE_USERS * i

            loop_users = self.search(
                    entity_type='user', start_index=start_index, max_results=loop_max_results, restriction=cql)

            print(".", end="", flush=True)
            return loop_users

        num_cores = cpu_count()
        pool = ThreadPool(processes=num_cores*2)
        loop_users_list = pool.map(search_users, [i for i in range(loop_count)])
        print("")  # new line
        users = [user for loop_users in loop_users_list for user in loop_users]
        return users

    def group_members(self, group_name: str, start_index: int = 0, max_results: int = 1000):
        api_url = self.host + f"/rest/usermanagement/1/group/user/direct" \
                              f"?groupname={group_name}&start-index={start_index}&max-results={max_results}"
        r = self.get(api_url, "Group members call failed")
        return r.json()

    def get_group_membership(self):
        api_url = self.host + '/rest/usermanagement/1/group/membership'
        self.headers = {'Accept': 'application/xml', 'Content-Type': 'application/xml'}
        response = self.get(api_url, 'Can not get group memberships')
        return response.content

    def get_server_info(self):
        api_url = self.host + '/rest/admin/1.0/server-info'
        response = self.get(api_url, 'Can not get Crowd server info')
        return response.json()

    def get_cluster_nodes(self):
        api_url = self.host + '/rest/atlassian-cluster-monitoring/cluster/nodes'
        response = self.get(api_url, 'Can not get Crowd cluster nodes information')
        return response.json()
