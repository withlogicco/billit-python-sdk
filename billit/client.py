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
    _args_api_mappings = {
        "customer_id": "customerId",
        "send_mail": "sendMail",
        "exclude_mydata": "excludeMydata",
        "invoice_date": "invoiceDate",
        "invoice_type_id": "invoiceTypeId",
        "is_paid": "isPaid",
        "mydata_invoice_type": "mydataInvoiceType",
        "taxes": "taxes",
        "products": "products",
        "tags": "tags",
        "mydata_payment": "mydataPayment",
        "mail_options": "mailOptions",
        "reminder": "reminder",
    }

    def list(self):
        return self.client._handle_request("GET", "/invoices")

    def create(
        self,
        customer_id: int,
        send_mail: bool,
        exclude_mydata: bool,
        invoice_date: str,
        invoice_type_id: int,
        is_paid: bool,
        mydata_invoice_type: str,
        taxes: Tax,
        products: list,
        tags: list,
        mydata_payment: dict,
        mail_options: str,
        reminder: bool,
    ):
        data = {
            self._args_api_mappings["customer_id"]: customer_id,
            self._args_api_mappings["send_mail"]: send_mail,
            self._args_api_mappings["exclude_mydata"]: exclude_mydata,
            self._args_api_mappings["invoice_date"]: invoice_date,
            self._args_api_mappings["invoice_type_id"]: invoice_type_id,
            self._args_api_mappings["is_paid"]: is_paid,
            self._args_api_mappings["mydata_invoice_type"]: mydata_invoice_type,
            self._args_api_mappings["taxes"]: dataclass.asdict(taxes),
            self._args_api_mappings["products"]: products,
            self._args_api_mappings["tags"]: tags,
            self._args_api_mappings["mydata_payment"]: mydata_payment,
            self._args_api_mappings["mail_options"]: mail_options,
            self._args_api_mappings["reminder"]: reminder,
        }

        return self.client._handle_request("POST", "/invoices", data=data)

    def show(self, uuid):
        return self.client._handle_request("GET", f"/invoices/{uuid}")

    def update(
        self,
        uuid,
        customer_id: int,
        send_mail: bool,
        exclude_mydata: bool,
        invoice_date: str,
        invoice_type_id: int,
        mydata_invoice_type: str,
        taxes: Tax,
        products: list,
        tags: list,
        mydata_payment: dict,
    ):

        data = {
            self._args_api_mappings["customer_id"]: customer_id,
            self._args_api_mappings["send_mail"]: send_mail,
            self._args_api_mappings["exclude_mydata"]: exclude_mydata,
            self._args_api_mappings["invoice_date"]: invoice_date,
            self._args_api_mappings["invoice_type_id"]: invoice_type_id,
            self._args_api_mappings["mydata_invoice_type"]: mydata_invoice_type,
            self._args_api_mappings["taxes"]: dataclass.asdict(taxes),
            self._args_api_mappings["products"]: products,
            self._args_api_mappings["tags"]: tags,
            self._args_api_mappings["mydata_payment"]: mydata_payment,
        }

        return self.client._handle_request("PUT", f"/invoices/{uuid}", data=data)

    def delete(self, uuid):
        return self.client._handle_request("DELETE", f"/invoices/{uuid}")
