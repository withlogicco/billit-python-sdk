import dataclasses
from typing import List

import requests

from billit.utils.tax_utils import Tax

from .auth import BillitAuthentication
from .constants import (
    PRODUCTION_BASE_URL,
    PRODUCTION_ENVIRONMENT,
    SANDBOX_BASE_URL,
    SANDBOX_ENVIRONMENT,
)
from .exceptions import APIError, AuthenticationError, InvalidEnvironment


class Client:
    """
    Base client for all API clients
    """

    def __init__(self, api_key, environment=PRODUCTION_ENVIRONMENT):
        self.api_key = api_key
        self.account = Account(self)
        self.invoices = Invoices(self)
        self.customers = Customers(self)
        self.contacts = Contacts(self)

        if environment not in [PRODUCTION_ENVIRONMENT, SANDBOX_ENVIRONMENT]:
            raise InvalidEnvironment(environment)

        if environment == PRODUCTION_ENVIRONMENT:
            self.base_url = PRODUCTION_BASE_URL
        else:
            self.base_url = SANDBOX_BASE_URL

    def _handle_response(self, response):

        if response.status_code == 401:
            raise AuthenticationError(response.json()["message"], response.status_code)

        if response.status_code == 204:
            return None

        try:
            response.raise_for_status()

            return response.json()
        except:
            error = f"{response.text}"
            if "application/json" in response.headers["Content-Type"]:
                resp = response.json()
                if "message" in resp:
                    error = f"Message: {resp.get('message')} , Error details: {resp.get('errors')}, {resp.get('data')}"
                    raise APIError(error, response)

                elif "msg" in resp:
                    error = f"Message: {resp.get('msg')} , Error details: {resp.get('errors')}, {resp.get('data')}"
                    raise APIError(error, response)

            raise APIError(error, response)

    def _handle_request(self, method, endpoint, params=None, data=None):
        url = self.base_url + endpoint
        response = requests.request(
            method,
            url,
            params=params,
            json=data,
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
        taxes: List[Tax],
        products: List,
        tags: List,
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
            self._args_api_mappings["taxes"]: [
                dataclasses.asdict(tax) for tax in taxes
            ],
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
        taxes: List[Tax],
        products: List,
        tags: List,
        mydata_payment: dict,
    ):

        data = {
            self._args_api_mappings["customer_id"]: customer_id,
            self._args_api_mappings["send_mail"]: send_mail,
            self._args_api_mappings["exclude_mydata"]: exclude_mydata,
            self._args_api_mappings["invoice_date"]: invoice_date,
            self._args_api_mappings["invoice_type_id"]: invoice_type_id,
            self._args_api_mappings["mydata_invoice_type"]: mydata_invoice_type,
            self._args_api_mappings["taxes"]: [
                dataclasses.asdict(tax) for tax in taxes
            ],
            self._args_api_mappings["products"]: products,
            self._args_api_mappings["tags"]: tags,
            self._args_api_mappings["mydata_payment"]: mydata_payment,
        }

        return self.client._handle_request("PUT", f"/invoices/{uuid}", data=data)

    def delete(self, uuid):
        return self.client._handle_request("DELETE", f"/invoices/{uuid}")


class Customers(SubClient):
    _args_api_mappings = {
        "is_company": "isCompany",
        "company": "company",
        "lang": "lang",
        "profession": "profession",
        "in_charge": "inCharge",
        "vat_id": "vatId",
        "tax_office": "taxOffice",
        "street_address": "streetAddress",
        "alias": "alias",
        "customer_type": "customerType",
        "postal_code": "postalCode",
        "city": "city",
        "country": "country",
        "mobile": "mobile",
        "phone": "phone",
        "fax": "fax",
        "info": "info",
        "public_note": "publicNote",
        "addresses": "addresses",
    }

    def list(self):
        return self.client._handle_request("GET", "/customers")

    def show(self, customer_id: int):
        return self.client._handle_request("GET", f"/customers/{customer_id}")

    def create(
        self,
        is_company: bool,
        company: str,
        lang: str,
        profession: str,
        in_charge: str,
        vat_id: str,
        tax_office: str,
        street_address: str,
        alias: str,
        customer_type: int,
        postal_code: str,
        city: str,
        country: str,
        mobile: str,
        phone: str,
        fax: str,
        info: str,
        public_note: str,
        addresses: List,
    ):
        data = {
            self._args_api_mappings["is_company"]: is_company,
            self._args_api_mappings["company"]: company,
            self._args_api_mappings["lang"]: lang,
            self._args_api_mappings["profession"]: profession,
            self._args_api_mappings["in_charge"]: in_charge,
            self._args_api_mappings["vat_id"]: vat_id,
            self._args_api_mappings["tax_office"]: tax_office,
            self._args_api_mappings["street_address"]: street_address,
            self._args_api_mappings["alias"]: alias,
            self._args_api_mappings["customer_type"]: customer_type,
            self._args_api_mappings["postal_code"]: postal_code,
            self._args_api_mappings["city"]: city,
            self._args_api_mappings["country"]: country,
            self._args_api_mappings["mobile"]: mobile,
            self._args_api_mappings["phone"]: phone,
            self._args_api_mappings["fax"]: fax,
            self._args_api_mappings["info"]: info,
            self._args_api_mappings["public_note"]: public_note,
            self._args_api_mappings["addresses"]: addresses,
        }
        print(data)
        return self.client._handle_request("POST", "/customers", data=data)

    def update(
        self,
        customer_id: int,
        is_company: bool,
        company: str,
        lang: str,
        profession: str,
        in_charge: str,
        vat_id: str,
        tax_office: str,
        street_address: str,
        alias: str,
        customer_type: int,
        postal_code: str,
        city: str,
        country: str,
        mobile: str,
        phone: str,
        fax: str,
        info: str,
        public_note: str,
        addresses: List,
    ):
        data = {
            self._args_api_mappings["is_company"]: is_company,
            self._args_api_mappings["company"]: company,
            self._args_api_mappings["lang"]: lang,
            self._args_api_mappings["profession"]: profession,
            self._args_api_mappings["in_charge"]: in_charge,
            self._args_api_mappings["vat_id"]: vat_id,
            self._args_api_mappings["tax_office"]: tax_office,
            self._args_api_mappings["street_address"]: street_address,
            self._args_api_mappings["alias"]: alias,
            self._args_api_mappings["customer_type"]: customer_type,
            self._args_api_mappings["postal_code"]: postal_code,
            self._args_api_mappings["city"]: city,
            self._args_api_mappings["country"]: country,
            self._args_api_mappings["mobile"]: mobile,
            self._args_api_mappings["phone"]: phone,
            self._args_api_mappings["fax"]: fax,
            self._args_api_mappings["info"]: info,
            self._args_api_mappings["public_note"]: public_note,
            self._args_api_mappings["addresses"]: addresses,
        }

        return self.client._handle_request(
            "PUT", f"/customers/{customer_id}", data=data
        )

    def delete(self, customer_id: int):
        return self.client._handle_request("DELETE", f"/customers/{customer_id}")


class Contacts(SubClient):
    DOMESTIC_CUSTOMER: int = 1
    INTRA_COMMUNITY_CUSTOMER: int = 2
    FOREIGN_CUSTOMER: int = 3
    PRIVATE_INDIVIDUAL: int = 4
    CUSTOMER: int = 1
    SUPPLIER: int = 2
    CUSTOMER_AND_SUPPLIER: int = 3
    _args_api_mappings = {
        "is_company": "isCompany",
        "company": "company",
        "lang": "lang",
        "profession": "profession",
        "in_charge": "inCharge",
        "vat_id": "vatId",
        "tax_office": "taxOffice",
        "street_address": "streetAddress",
        "alias": "alias",
        "customer_type": "customerType",
        "postal_code": "postalCode",
        "city": "city",
        "country": "country",
        "mobile": "mobile",
        "phone": "phone",
        "fax": "fax",
        "info": "info",
        "public_note": "publicNote",
        "contact_type": "contactType",
        "currency": "currency",
        "addresses": "addresses",
    }

    def list(self):
        return self.client._handle_request("GET", "/contacts")

    def show(self, contact_id: int):
        return self.client._handle_request("GET", f"/contacts/{contact_id}")

    def create(
        self,
        is_company: bool,
        company: str,
        lang: str,
        profession: str,
        in_charge: str,
        vat_id: str,
        tax_office: str,
        street_address: str,
        alias: str,
        customer_type: int,
        postal_code: str,
        city: str,
        country: str,
        mobile: str,
        phone: str,
        fax: str,
        info: str,
        public_note: str,
        contact_type: str,
        currency: str,
        addresses: List,
    ):
        data = {
            self._args_api_mappings["is_company"]: is_company,
            self._args_api_mappings["company"]: company,
            self._args_api_mappings["lang"]: lang,
            self._args_api_mappings["profession"]: profession,
            self._args_api_mappings["in_charge"]: in_charge,
            self._args_api_mappings["vat_id"]: vat_id,
            self._args_api_mappings["tax_office"]: tax_office,
            self._args_api_mappings["street_address"]: street_address,
            self._args_api_mappings["alias"]: alias,
            self._args_api_mappings["customer_type"]: customer_type,
            self._args_api_mappings["postal_code"]: postal_code,
            self._args_api_mappings["city"]: city,
            self._args_api_mappings["country"]: country,
            self._args_api_mappings["mobile"]: mobile,
            self._args_api_mappings["phone"]: phone,
            self._args_api_mappings["fax"]: fax,
            self._args_api_mappings["info"]: info,
            self._args_api_mappings["public_note"]: public_note,
            self._args_api_mappings["contact_type"]: contact_type,
            self._args_api_mappings["currency"]: currency,
            self._args_api_mappings["addresses"]: addresses,
        }

        return self.client._handle_request("POST", "/contacts", data=data)

    def update(
        self,
        contact_id: int,
        is_company: bool,
        company: str,
        lang: str,
        profession: str,
        in_charge: str,
        vat_id: str,
        tax_office: str,
        street_address: str,
        alias: str,
        customer_type: int,
        postal_code: str,
        city: str,
        country: str,
        mobile: str,
        phone: str,
        fax: str,
        info: str,
        public_note: str,
        contact_type: str,
        currency: str,
        addresses: List,
    ):
        data = {
            self._args_api_mappings["is_company"]: is_company,
            self._args_api_mappings["company"]: company,
            self._args_api_mappings["lang"]: lang,
            self._args_api_mappings["profession"]: profession,
            self._args_api_mappings["in_charge"]: in_charge,
            self._args_api_mappings["vat_id"]: vat_id,
            self._args_api_mappings["tax_office"]: tax_office,
            self._args_api_mappings["street_address"]: street_address,
            self._args_api_mappings["alias"]: alias,
            self._args_api_mappings["customer_type"]: customer_type,
            self._args_api_mappings["postal_code"]: postal_code,
            self._args_api_mappings["city"]: city,
            self._args_api_mappings["country"]: country,
            self._args_api_mappings["mobile"]: mobile,
            self._args_api_mappings["phone"]: phone,
            self._args_api_mappings["fax"]: fax,
            self._args_api_mappings["info"]: info,
            self._args_api_mappings["public_note"]: public_note,
            self._args_api_mappings["contact_type"]: contact_type,
            self._args_api_mappings["currency"]: currency,
            self._args_api_mappings["addresses"]: addresses,
        }

        return self.client._handle_request("PUT", f"/contacts/{contact_id}", data=data)

    def delete(self, contact_id: int):
        return self.client._handle_request("DELETE", f"/contacts/{contact_id}")
