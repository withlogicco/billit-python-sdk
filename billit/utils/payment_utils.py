from dataclasses import dataclass


@dataclass
class PaidInvoice:
    id: int = 0
    label: int = 0
    unpaidAmount: int = 0
    paymentAmount: int = 0
