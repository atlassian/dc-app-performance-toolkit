from util.api.abstract_clients import JSM_EXPERIMENTAL_HEADERS
from util.api.abstract_clients import RestClient
from selenium_ui.conftest import retry

BATCH_SIZE_USERS = 1000


class JsmRestClient(RestClient):

    def get_agent(self, username='.', start_at=0, max_results=1000, include_active=True, include_inactive=False):
        """
        Returns a list of users that match the search string. This resource cannot be accessed anonymously.
        :param username: A query string used to search username, name or e-mail address. "." - search for all users.
        :param start_at: the index of the first user to return (0-based).
        :param max_results: the maximum number of users to return (defaults to 50).
        The maximum allowed value is 1000.
        If you specify a value that is higher than this number, your search results will be truncated.
        :param include_active: If true, then active users are included in the results (default true)
        :param include_inactive: If true, then inactive users are included in the results (default false)
        :return: Returns the requested users
        """

        loop_count = max_results // BATCH_SIZE_USERS + 1
        last_loop_remainder = max_results % BATCH_SIZE_USERS

        users_list = list()
        max_results = BATCH_SIZE_USERS if max_results > BATCH_SIZE_USERS else max_results

        while loop_count > 0:
            api_url = f'{self.host}/rest/api/2/user/search?username={username}&startAt={start_at}' \
                      f'&maxResults={max_results}&includeActive={include_active}&includeInactive={include_inactive}'
            response = self.get(api_url, "Could not retrieve users")

            users_list.extend(response.json())
            loop_count -= 1
            start_at += len(response.json())
            if loop_count == 1:
                max_results = last_loop_remainder

        return users_list

    def create_customer(self, email=None, full_name=None):
        """
        Creates a customer that is not associated with a service desk project.
        :param email
        :param full_name
        """
        api_url = self.host + "/rest/servicedeskapi/customer"
        payload = {
            "email": email,
            "fullName": full_name
        }
        jsm_headers = JSM_EXPERIMENTAL_HEADERS
        response = self.post(api_url, "Could not create jsm customer", body=payload, headers=jsm_headers)

        return response.json()

    def create_request(self, service_desk_id: int, request_type_id: int,
                       request_fields_values: dict, request_participants: list, raise_on_behalf_of: str):
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
            "requestFieldValues": request_fields_values,
            "requestParticipants": request_participants,
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

    def get_request_type_fields(self, service_desk_id, request_type_id):
        """
        Returns the fields for a request type, for a given request type Id and service desk Id.
        These are the fields that are required to create a customer request of that particular request type.
        :param service_desk_id:
        :param request_type_id:
        :return:
        """
        api_url = self.host + f"/rest/servicedeskapi/servicedesk/{service_desk_id}/requesttype/{request_type_id}/field"
        response = self.get(api_url, f"Could not get request type fields for a "
                                     f"service desk id {service_desk_id} and request type is {request_type_id}")
        return response.json()['requestTypeFields']

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
    def get_servicedesk_info(self):
        """
        This resource represents the Jira Service Desk application.
        :return:
        """
        api_url = self.host + "/rest/servicedeskapi/info"
        response = self.get(api_url, "Could not get request Service desk info.")
        return response

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

    def attach_temp_files(self, service_desk_id, file_paths: dict, auth: tuple = None):
        """
        Create one or more temporary attachments, which can later be converted into permanent
        attachments on Create attachment.
        :param service_desk_id:
        :param file_paths:
        :param auth:
        :return:
        """
        api_url = self.host + f"/rest/servicedeskapi/servicedesk/{service_desk_id}/attachTemporaryFile"
        headers = {'X-Atlassian-Token': 'no-check', 'X-ExperimentalApi': 'opt-in'}
        files = [('file', open(file, 'rb')) for file in file_paths]
        response = self.post(api_url, "Could not create temporary attachment", headers=headers, files=files, auth=auth)
        return response.json()['temporaryAttachments']

    def create_attachments(self, issue_id_or_key: str, temporary_attachment_ids: list, public: bool = True,
                           additional_comment: str = "", auth: tuple = None):
        """
        Adds one or more temporary attachments that were created using Attach temporary file to a customer request.
        The attachment visibility is set by the public field.
        :param issue_id_or_key
        :param temporary_attachment_ids:
        :param public:
        :param additional_comment:
        :param auth:
        :return:
        """
        api_url = self.host + f"/rest/servicedeskapi/request/{issue_id_or_key}/attachment"
        payload = {
            "temporaryAttachmentIds": temporary_attachment_ids,
            "public": public,
            "additionalComment": {"body": additional_comment}
        }
        jsm_headers = JSM_EXPERIMENTAL_HEADERS
        response = self.post(api_url, "Could not create attachment from temp attach ids: {temporary_attachment_ids}.",
                             body=payload, headers=jsm_headers, auth=auth)
        return response.json()

    def create_comment(self, issue_id_or_key: str, public: bool = True, text: str = "", auth: tuple = None):
        """
        This resource represents the comments on a customer request.
        :param issue_id_or_key:
        :param public:
        :param text:
        :param auth:
        :return:
        """
        api_url = self.host + f"/rest/servicedeskapi/request/{issue_id_or_key}/comment"
        payload = {
            "body": text,
            "public": public
        }
        jsm_headers = JSM_EXPERIMENTAL_HEADERS
        response = self.post(api_url, "Could not create comment for issue id/key: {issue_id_or_key}.",
                             body=payload, headers=jsm_headers, auth=auth)
        return response.json()

    def get_request_transactions(self, issue_id_or_key: str, auth: tuple = None):
        """
        Returns a list of transitions that customers can perform on the request.
        :param issue_id_or_key:
        :param auth:
        :return:
        """
        api_url = self.host + f"/rest/servicedeskapi/request/{issue_id_or_key}/transition"
        jsm_headers = JSM_EXPERIMENTAL_HEADERS
        response = self.get(api_url,
                            f"Could not get transactions for issue id/key: {issue_id_or_key}.",
                            headers=jsm_headers, auth=auth)
        return response.json()

    def request_transition(self, issue_id_or_key: str, transition_id: str, additional_comment: str = None,
                           auth: tuple = None):
        """
        Perform a customer transition for a given request and transition ID.
        An optional comment can be included to provide a reason for the transition.
        :param issue_id_or_key:
        :param transition_id:
        :param additional_comment:
        :param auth:
        :return:
        """
        api_url = self.host + f"/rest/servicedeskapi/request/{issue_id_or_key}/transition"
        payload = {
            "id": transition_id,
        }
        if additional_comment:
            payload['additionalComment'] = {"body": additional_comment}
        jsm_headers = JSM_EXPERIMENTAL_HEADERS
        response = self.post(
            api_url, f"Could not make transition for issue id/key: {issue_id_or_key} to transition_id: {transition_id}",
            body=payload, headers=jsm_headers, auth=auth)
        return response

    def get_request_status(self, issue_id_or_key: str, auth: tuple = None):
        """
        Returns a list of transitions that customers can perform on the request.
        :param issue_id_or_key:
        :param auth:
        :return:
        """
        api_url = self.host + f"/rest/servicedeskapi/request/{issue_id_or_key}/status"
        jsm_headers = JSM_EXPERIMENTAL_HEADERS
        response = self.get(api_url,
                            f"Could not get transactions for issue id/key: {issue_id_or_key}.",
                            headers=jsm_headers, auth=auth)
        return response.json()

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
