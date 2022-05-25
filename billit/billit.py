import os

import requests
from dotenv import load_dotenv

from constants import SANDBOX_BASE_URL

load_dotenv()


class Client:
    """
    Base client for all API clients
    """

    def __init__(self, api_key):
        self.api_key = api_key or os.environ.get("BILLIT_API_KEY")
        self.base_url = SANDBOX_BASE_URL
        self.account = Account(self)

    def _request(self, method, endpoint, params=None, data=None):
        headers = {
            "Content-Type": "application/json",
            "Accept": "",
            "Authorization": "Bearer {}".format(self.api_key),
        }
        url = SANDBOX_BASE_URL + endpoint
        response = requests.request(
            method, url, params=params, data=data, headers=headers
        )
        return response.json()


# Use this for everything
class SubClient:
    client: Client

    def __init__(self, client: Client):
        self.client = client


class Account(SubClient):
    # TODO: Implement this
    def my(self):
        return self.client._request("GET", "/account")
