from typing import Protocol

from .domain006 import Customer


class CustomerRepository(Protocol):
    async def save(self, customer: Customer) -> None:
        ...

    async def get(self, customer_id: str) -> Customer:
        ...
