from requests.auth import AuthBase


class BillitAuthentication(AuthBase):
    """
    Authentication handler for Billit API
    """

    def __init__(self, api_key):
        self.api_key = api_key

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.api_key}"
        return r
