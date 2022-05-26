import requests

from .auth import BillitAuthentication
from .constants import (
    PRODUCTION_BASE_URL,
    PRODUCTION_ENVIRONMENT,
    SANDBOX_BASE_URL,
    SANDBOX_ENVIRONMENT,
)
from .error import ApiError, AuthenticationError, InvalidEnvironment


class Client:
    """
    Base client for all API clients
    """

    def __init__(self, api_key, environment=PRODUCTION_ENVIRONMENT):
        self.api_key = api_key
        self.account = Account(self)

        if environment not in [PRODUCTION_ENVIRONMENT, SANDBOX_ENVIRONMENT]:
            raise InvalidEnvironment(environment)

        if environment == PRODUCTION_ENVIRONMENT:
            self.base_url = PRODUCTION_BASE_URL
        else:
            self.base_url = SANDBOX_BASE_URL

    def _handle_response(self, response):
        if response.status_code == 401:
            raise AuthenticationError(response.json()["message"], response.status_code)

        try:
            response.raise_for_status()

            return response.json()
        except:
            error = f"{response.text}"
            if "application/json" in response.headers["Content-Type"]:
                error = f"{response.json()['message']}"

            raise ApiError(error, response.status_code)

    def _handle_request(self, method, endpoint, params=None, data=None):
        url = self.base_url + endpoint
        response = requests.request(
            method,
            url,
            params=params,
            data=data,
            auth=BillitAuthentication(self.api_key),
        )
        return self._handle_response(response)


# Use this for everything
class SubClient:
    client: Client

    def __init__(self, client: Client):
        self.client = client


class Account(SubClient):
    def my(self):
        return self.client._handle_request("GET", "/account")
