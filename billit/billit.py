import requests

from auth import BillitAuthentication
from constants import (
    PRODUCTION_BASE_URL,
    PRODUCTION_ENVIRONMENT,
    SANDBOX_BASE_URL,
    SANDBOX_ENVIRONMENT,
)


class Client:
    """
    Base client for all API clients
    """

    def __init__(self, api_key, environment=PRODUCTION_ENVIRONMENT):
        self.api_key = api_key
        self.account = Account(self)

        if environment not in [PRODUCTION_ENVIRONMENT, SANDBOX_ENVIRONMENT]:
            raise Exception(f"Invalid environment provided: {environment}")

        if environment == PRODUCTION_ENVIRONMENT:
            self.base_url = PRODUCTION_BASE_URL
        else:
            self.base_url = SANDBOX_BASE_URL

    def _handle_response(self, response):
        if response.status_code == 401:
            raise Client.AuthenticationError(response.json()["message"])

        try:
            response.raise_for_status()

            return response.json()
        except:
            if "application/json" in response.headers["Content-Type"]:
                error = f"Error code: {response.status_code}, Error message: {response.json()['message']}"
            else:
                error = f"Error code: {response.status_code}, error message: {response.text}"

            return Client.ApiError(error, response.status_code)

    def _request(self, method, endpoint, params=None, data=None):
        url = self.base_url + endpoint
        response = requests.request(
            method,
            url,
            params=params,
            data=data,
            auth=BillitAuthentication(self.api_key),
        )
        return self._handle_response(response)

    class AuthenticationError(Exception):
        pass

    class ApiError(Exception):
        def __init__(self, error_message, response_status_code=None):
            Exception.__init__(self, error_message)
            self.response_status_code = response_status_code


# Use this for everything
class SubClient:
    client: Client

    def __init__(self, client: Client):
        self.client = client


class Account(SubClient):
    def my(self):
        return self.client._request("GET", "/account")
