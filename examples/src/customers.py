import uuid
from datetime import datetime, timezone

import structlog
import tomodachi
from aiohttp import web
from pydantic import BaseModel
from tomodachi.envelope.json_base import JsonBase

from .adapters import aws, config, dynamodb
from .utils.logger import configure_logger

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class Order(BaseModel):
    order_id: str

    def to_dict(self) -> dict:
        return {"order_id": self.order_id}


class OrderCreatedEvent(BaseModel):
    event_id: str
    order_id: str
    customer_id: str

    @staticmethod
    def from_dict(event: dict) -> "OrderCreatedEvent":
        return OrderCreatedEvent(
            event_id=event["event_id"],
            order_id=event["order_id"],
            customer_id=event["customer_id"],
        )


class Customer(BaseModel):
    customer_id: str
    name: str
    orders: list[Order]
    created_at: datetime

    def to_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "orders": [order.to_dict() for order in self.orders],
            "created_at": self.created_at.isoformat(),
        }


class Service(tomodachi.Service):
    name = "service-customers"

    options = config.create_tomodachi_options()

    async def _start_service(self) -> None:
        configure_logger()
        self._dynamodb_client, self._dynamodb_client_exit_stack = await aws.create_dynamodb_client()
        await dynamodb.create_dynamodb_table(self._dynamodb_client)

    async def _stop_service(self) -> None:
        await self._dynamodb_client_exit_stack.aclose()

    @tomodachi.http("GET", r"/health/?")
    async def healthcheck(self, request: web.Request) -> web.Response:
        return web.json_response(data={"status": "ok"})

    @tomodachi.http("POST", r"/customer/?")
    async def create_customer(self, request: web.Request) -> web.Response:
        data = await request.json()

        customer = Customer(
            customer_id=str(uuid.uuid4()),
            name=data["name"],
            orders=[],
            created_at=datetime.now(timezone.utc),
        )

        await self._dynamodb_client.put_item(
            TableName=dynamodb.get_table_name(),
            Item={
                "PK": {"S": f"CUSTOMER#{customer.customer_id}"},
                "CustomerId": {"S": customer.customer_id},
                "Name": {"S": customer.name},
                "CreatedAt": {"S": customer.created_at.isoformat()},
            },
            ConditionExpression="attribute_not_exists(PK)",
        )

        logger.info("customer_created", customer_id=customer.customer_id)
        return web.json_response({**customer.to_dict()})

    @tomodachi.http("GET", r"/customer/(?P<customer_id>[^/]+?)/?")
    async def get_customer(self, request: web.Request, customer_id: str) -> web.Response:
        response = await self._dynamodb_client.get_item(
            TableName=dynamodb.get_table_name(),
            Key={"PK": {"S": f"CUSTOMER#{customer_id}"}},
        )
        item = response.get("Item")
        if not item:
            logger.error("customer_not_found", customer_id=customer_id)
            return web.json_response({"error": "CUSTOMER_NOT_FOUND"}, status=404)

        orders = item["Orders"]["SS"] if "Orders" in item else []
        customer = Customer(
            customer_id=item["CustomerId"]["S"],
            name=item["Name"]["S"],
            orders=[Order(order_id=order_id) for order_id in orders],
            created_at=datetime.fromisoformat(item["CreatedAt"]["S"]),
        )

        return web.json_response(customer.to_dict())

    @tomodachi.aws_sns_sqs(
        "order--created",
        queue_name="customer--order-created",
        message_envelope=JsonBase,
    )
    async def handle_order_created(self, data: dict) -> None:
        event = OrderCreatedEvent.from_dict(data)
        await self._dynamodb_client.update_item(
            TableName=dynamodb.get_table_name(),
            Key={"PK": {"S": f"CUSTOMER#{event.customer_id}"}},
            UpdateExpression="ADD Orders :orders",
            ExpressionAttributeValues={":orders": {"SS": [event.order_id]}},
            ConditionExpression="attribute_exists(PK)",
        )
        logger.info(
            "order_created",
            order_id=event.order_id,
            customer_id=event.customer_id,
            event_id=event.event_id,
        )
