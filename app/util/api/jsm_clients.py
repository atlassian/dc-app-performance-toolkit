from util.api.abstract_clients import JSM_EXPERIMENTAL_HEADERS
from util.api.abstract_clients import RestClient
from selenium_ui.conftest import retry

BATCH_SIZE_USERS = 1000


class JsmRestClient(RestClient):

    def create_request(self, service_desk_id: int, request_type_id: int, raise_on_behalf_of: str):
        """
        Creates a customer request in a service desk.
        :param service_desk_id:
        :param request_type_id:
        :param request_fields_values:
        :param request_participants:
        :param raise_on_behalf_of:
        :return:
        """
        api_url = self.host + "/rest/servicedeskapi/request"
        payload = {
            "serviceDeskId": service_desk_id,
            "requestTypeId": request_type_id,
            "requestFieldValues": {
                "description": "I need a new request",
                "summary": "Request via REST"},
            "raiseOnBehalfOf": raise_on_behalf_of
        }
        jsm_headers = JSM_EXPERIMENTAL_HEADERS
        response = self.post(api_url, "Could not create jsm request", body=payload, headers=jsm_headers)

        return response.json()

    def get_request(self, issue_id_or_key: str, auth: tuple = None):
        api_url = self.host + f"/rest/servicedeskapi/request/{issue_id_or_key}"
        response = self.get(api_url, f"Could not get customer request for id/key {issue_id_or_key}", auth=auth)
        return response.json()

    def get_requests(self, start_at: int = 0, max_results: int = 100, auth: tuple = None, status: str = None):
        """
        Returns the customer request for a given request Id/key.
        :param issue_id_or_key:
        :param auth:
        :param start_at:
        :param max_results:
        :param status:
        :return:
        """
        BATCH_REQUEST_SIZE = 100
        loop_count = max_results // BATCH_REQUEST_SIZE + 1
        last_loop_remainder = max_results % BATCH_REQUEST_SIZE

        max_results = BATCH_REQUEST_SIZE if max_results > BATCH_REQUEST_SIZE else max_results
        requests = []

        init_url = self.host + "/rest/servicedeskapi/request"
        while loop_count > 0:

            api_url = init_url + f"?start={start_at}&limit={max_results}"
            if status:
                api_url += f"&requestStatus={status}"

            response = self.get(api_url, f"Could not get customer requests ", auth=auth)
            values = response.json()['values']
            requests.extend(values)

            if 'isLastPage' in response.json() and response.json()['isLastPage']:
                break

            loop_count -= 1
            start_at += len(values)
            if loop_count == 1:
                max_results = last_loop_remainder
        return requests

    @retry()
    def get_queue(self, service_desk_id: int, start: int = 0):
        """
        Returns the customer request for a given request Id/key.
        :param service_desk_id:
        :param start: the index of the first user to return (0-based).
        :return:
        """
        api_url = self.host + f"/rest/servicedeskapi/servicedesk/{service_desk_id}/queue?start={start}"
        response = self.get(api_url, f"Could not get queues for service desk {service_desk_id}")
        return response.json()['values']

    @retry()
    def get_request_types(self, service_desk_id):
        """
        Returns all request types from a service desk, for a given service desk Id.
        :param service_desk_id:
        :return:
        """
        api_url = self.host + f"/rest/servicedeskapi/servicedesk/{service_desk_id}/requesttype"
        response = self.get(api_url, f"Could not get request types for service desk id {service_desk_id}")
        return response.json()['values']

    @retry()
    def get_all_service_desks(self):
        """
        Returns all service desks in the Jira Service Desk application.
        :return:
        """
        start = 0
        limit = 100
        finished = False
        results = []
        while not finished:
            api_url = self.host + f"/rest/servicedeskapi/servicedesk?start={start}&limit={limit}"
            r = self.get(api_url, "Could not get all service desks").json()
            results.extend(r['values'])
            if r['isLastPage']:
                finished = True
            else:
                start = start + limit
        return results

    @retry()
    def get_service_desk_reports(self, project_key: str = ''):
        api_url = self.host + f"/rest/servicedesk/1/{project_key}/webfragments/sections/sd-reports-nav-custom-section"
        payload = {
            "projectKey": project_key
        }
        response = self.post(api_url, "Could not get Service Desk reports info", body=payload)
        custom_reports_list = []
        for report in response.json():
            if 'label' in report.keys():
                if report['label'] == 'Custom':
                    custom_reports_list = report['items']
        if not custom_reports_list:
            raise Exception(f"Could not get Service Desk reports info for project {project_key}")
        return custom_reports_list

    def get_all_organizations(self, max_count: int = None, auth: tuple = None):
        """
        Get all organizations
        :param max_count:
        :param auth:
        :return:
        """
        jsm_headers = JSM_EXPERIMENTAL_HEADERS

        start = 0
        limit = 50
        finished = False
        results = []
        while not finished:
            api_url = self.host + f"/rest/servicedeskapi/organization?start={start}&limit={limit}"
            r = self.get(api_url, "Could not get all organisations", headers=jsm_headers, auth=auth).json()
            results.extend(r['values'])
            if r['isLastPage']:
                finished = True
            else:
                start = start + limit

        if max_count:
            return results[:max_count]
        return results

    def get_all_users_in_organization(self, org_id: int, max_count: int = None):
        """
        Get all user in organization
        :param org_id:
        :param max_count:
        :param auth:
        :return:
        """
        jsm_headers = JSM_EXPERIMENTAL_HEADERS

        start = 0
        limit = 50
        finished = False
        results = []
        while not finished:
            api_url = self.host + f"/rest/servicedeskapi/organization/{org_id}/user?start={start}&limit={limit}"
            r = self.get(api_url, "Could not get all organisations", headers=jsm_headers).json()
            results.extend(r['values'])
            if r['isLastPage']:
                finished = True
            else:
                start = start + limit

        if max_count:
            return results[:max_count]
        return results

    def get_all_schemas(self):
        objectschemas = []
        api_url = self.host + "/rest/insight/1.0/objectschema/list?"
        r = self.get(api_url,
                     f"Could not get objectSchemas id").json()
        objectschemas.extend(r['objectschemas'])
        return objectschemas
