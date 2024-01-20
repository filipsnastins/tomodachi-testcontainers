from dataclasses import dataclass


@dataclass
class Order:
    order_id: str

    def to_dict(self) -> dict:
        return {"order_id": self.order_id}


@dataclass
class OrderCreatedEvent:
    order_id: str
    customer_id: str

    @staticmethod
    def from_dict(event: dict) -> "OrderCreatedEvent":
        return OrderCreatedEvent(
            order_id=event["order_id"],
            customer_id=event["customer_id"],
        )


@dataclass
class Customer:
    customer_id: str
    name: str
    orders: list[Order]

    def to_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "orders": [order.to_dict() for order in self.orders],
        }


@dataclass
class CustomerCreatedEvent:
    customer_id: str
    name: str

    @staticmethod
    def from_customer(customer: Customer) -> "CustomerCreatedEvent":
        return CustomerCreatedEvent(
            customer_id=customer.customer_id,
            name=customer.name,
        )

    def to_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "name": self.name,
        }
