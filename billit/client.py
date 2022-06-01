from dataclasses import dataclass
import requests

from billit.utils.tax_utils import Tax

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
        self.invoices = Invoices(self)

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


class SubClient:
    client: Client

    def __init__(self, client: Client):
        self.client = client


class Account(SubClient):
    def my(self):
        return self.client._handle_request("GET", "/account")


class Invoices(SubClient):
    def list(self):
        return self.client._handle_request("GET", "/invoices")

    def create(
        self,
        customerId: int,
        sendMail: bool,
        excludeMydata: bool,
        invoiceDate: str,
        invoiceTypeId: int,
        isPaid: bool,
        mydataInvoiceType: str,
        taxes: Tax,
        products: list,
        tags: list,
        mydataPayment: dict,
        mailOptions: str,
        reminder: bool,
    ):
        data = {
            "customerId": customerId,
            "sendMail": sendMail,
            "excludeMydata": excludeMydata,
            "invoiceDate": invoiceDate,
            "invoiceTypeId": invoiceTypeId,
            "isPaid": isPaid,
            "mydataInvoiceType": mydataInvoiceType,
            "taxes": dataclass.asdict(taxes),
            "products": products,
            "tags": tags,
            "mydataPayment": mydataPayment,
            "mailOptions": mailOptions,
            "reminder": reminder,
        }

        return self.client._handle_request("POST", "/invoices", data=data)

    def show(self, uuid):
        return self.client._handle_request("GET", f"/invoices/{uuid}")

    def update(
        self,
        uuid,
        customerId: int,
        sendMail: bool,
        excludeMydata: bool,
        invoiceDate: str,
        invoiceTypeId: int,
        mydataInvoiceType: str,
        taxes: Tax,
        products: list,
        tags: list,
        mydataPayment: dict,
    ):
        data = {
            "customerId": customerId,
            "sendMail": sendMail,
            "excludeMydata": excludeMydata,
            "invoiceDate": invoiceDate,
            "invoiceTypeId": invoiceTypeId,
            "mydataInvoiceType": mydataInvoiceType,
            "taxes": dataclass.asdict(taxes),
            "products": products,
            "tags": tags,
            "mydataPayment": mydataPayment,
        }

        return self.client._handle_request("PUT", f"/invoices/{uuid}", data=data)

    def delete(self, uuid):
        return self.client._handle_request("DELETE", f"/invoices/{uuid}")
