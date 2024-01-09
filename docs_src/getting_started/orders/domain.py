from dataclasses import dataclass


@dataclass
class Order:
    id: str
    customer_id: str
    product: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "product": self.product,
        }
