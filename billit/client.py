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
        self.ocp = OCP(self)
        self.products = Products(self)

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
    DOMESTIC_CUSTOMER: int = 1
    INTRA_COMMUNITY_CUSTOMER: int = 2
    FOREIGN_CUSTOMER: int = 3
    PRIVATE_INDIVIDUAL: int = 4
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


class OCP(SubClient):
    _args_api_mappings = {
        "title": "title",
        "description": "description",
        "cost": "cost",
        "customer_id": "customerId",
        "invoice_type_id": "invoiceTypeId",
        "net_value": "netValue",
        "vat_id": "vatId",
        "product_id": "productId",
        "payment_method_id": "paymentMethodId",
        "lang": "lang",
        "expiration_at": "expirationAt",
    }

    def list(self):
        return self.client._handle_request("GET", "/ocps")

    def show(self, ocp_id: str):
        return self.client._handle_request("GET", f"/ocps/{ocp_id}")

    def create(
        self,
        title: str,
        description: str,
        cost: int,
        customer_id: int,
        invoice_type_id: int,
        net_value: int,
        vat_id: int,
        product_id: int,
        payment_method_id: int,
        lang: str,
        expiration_at: str,
    ):
        data = {
            self._args_api_mappings["title"]: title,
            self._args_api_mappings["description"]: description,
            self._args_api_mappings["cost"]: cost,
            self._args_api_mappings["customer_id"]: customer_id,
            self._args_api_mappings["invoice_type_id"]: invoice_type_id,
            self._args_api_mappings["net_value"]: net_value,
            self._args_api_mappings["vat_id"]: vat_id,
            self._args_api_mappings["product_id"]: product_id,
            self._args_api_mappings["payment_method_id"]: payment_method_id,
            self._args_api_mappings["lang"]: lang,
            self._args_api_mappings["expiration_at"]: expiration_at,
        }

        return self.client._handle_request("POST", "/ocps", data=data)

    def update(
        self,
        ocp_id: str,
        title: str,
        description: str,
        cost: int,
        customer_id: int,
        invoice_type_id: int,
        net_value: int,
        vat_id: int,
        product_id: int,
        payment_method_id: int,
        lang: str,
        expiration_at: str,
    ):
        data = {
            self._args_api_mappings["title"]: title,
            self._args_api_mappings["description"]: description,
            self._args_api_mappings["cost"]: cost,
            self._args_api_mappings["customer_id"]: customer_id,
            self._args_api_mappings["invoice_type_id"]: invoice_type_id,
            self._args_api_mappings["net_value"]: net_value,
            self._args_api_mappings["vat_id"]: vat_id,
            self._args_api_mappings["product_id"]: product_id,
            self._args_api_mappings["payment_method_id"]: payment_method_id,
            self._args_api_mappings["lang"]: lang,
            self._args_api_mappings["expiration_at"]: expiration_at,
        }

        return self.client._handle_request("PUT", f"/ocps/{ocp_id}", data=data)

    def delete(self, ocp_id: str):
        return self.client._handle_request("DELETE", f"/ocps/{ocp_id}")


class Products(SubClient):
    _args_api_mappings = {
        "name": "name",
        "description": "description",
        "name_sec": "nameSec",
        "description_sec": "descriptionSec",
        "unit_price": "unitPrice",
        "default_vat_id": "defaultVatId",
        "stock": "stock",
        "with_stock": "withStock",
        "is_vat_included": "isVatIncluded",
        "active": "active",
    }

    def list(self):
        return self.client._handle_request("GET", "/products")

    def show(self, product_id: str):
        return self.client._handle_request("GET", f"/products/{product_id}")

    def create(
        self,
        name: str,
        description: str,
        name_sec: str,
        description_sec: str,
        unit_price: int,
        default_vat_id: int,
        stock: int,
        with_stock: bool,
        is_vat_included: bool,
        active: bool,
    ):
        data = {
            self._args_api_mappings["name"]: name,
            self._args_api_mappings["description"]: description,
            self._args_api_mappings["name_sec"]: name_sec,
            self._args_api_mappings["description_sec"]: description_sec,
            self._args_api_mappings["unit_price"]: unit_price,
            self._args_api_mappings["default_vat_id"]: default_vat_id,
            self._args_api_mappings["stock"]: stock,
            self._args_api_mappings["with_stock"]: with_stock,
            self._args_api_mappings["is_vat_included"]: is_vat_included,
            self._args_api_mappings["active"]: active,
        }

        return self.client._handle_request("POST", "/products", data=data)

    def update(
        self,
        product_id: str,
        name: str,
        description: str,
        name_sec: str,
        description_sec: str,
        unit_price: int,
        default_vat_id: int,
        stock: int,
        with_stock: bool,
        is_vat_included: bool,
        active: bool,
    ):
        data = {
            self._args_api_mappings["name"]: name,
            self._args_api_mappings["description"]: description,
            self._args_api_mappings["name_sec"]: name_sec,
            self._args_api_mappings["description_sec"]: description_sec,
            self._args_api_mappings["unit_price"]: unit_price,
            self._args_api_mappings["default_vat_id"]: default_vat_id,
            self._args_api_mappings["stock"]: stock,
            self._args_api_mappings["with_stock"]: with_stock,
            self._args_api_mappings["is_vat_included"]: is_vat_included,
            self._args_api_mappings["active"]: active,
        }

        return self.client._handle_request("PUT", f"/products/{product_id}", data=data)

    def delete(self, product_id: str):
        return self.client._handle_request("DELETE", f"/products/{product_id}")
