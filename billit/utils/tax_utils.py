from dataclasses import asdict, dataclass


@dataclass
class Tax:
    taxId: int = 0
    taxVatShow: int = 0

    # return a dict
    def as_dict(self):
        return asdict(self)
