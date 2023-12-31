import uuid
from dataclasses import dataclass


@dataclass
class Customer:
    id: str
    name: str
    email: str

    @staticmethod
    def create(name: str, email: str) -> "Customer":
        return Customer(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
        )
