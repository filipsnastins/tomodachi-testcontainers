import uuid

from .credit_check import verify_customer_credit
from .domain import Order


async def create_new_order(customer_id: str, product: str) -> Order:
    order = Order(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        product=product,
    )
    await verify_customer_credit(order.customer_id)
    return order
