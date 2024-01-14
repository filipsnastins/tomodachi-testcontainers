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
    customer_id: str
    products: list[str]
    created_at: datetime

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "products": self.products,
            "created_at": self.created_at.isoformat(),
        }


class OrderCreatedEvent(BaseModel):
    event_id: str
    order_id: str
    customer_id: str
    products: list[str]
    created_at: datetime

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "products": self.products,
            "created_at": self.created_at.isoformat(),
        }


class Service(tomodachi.Service):
    name = "service-orders"

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

    @tomodachi.http("POST", r"/order/?")
    async def create_order(self, request: web.Request) -> web.Response:
        data = await request.json()
        customer_id: str = data["customer_id"]
        products: list[str] = data["products"]

        order = Order(
            order_id=str(uuid.uuid4()),
            customer_id=customer_id,
            products=products,
            created_at=datetime.now(timezone.utc),
        )
        event = OrderCreatedEvent(
            event_id=str(uuid.uuid4()),
            customer_id=customer_id,
            order_id=order.order_id,
            products=order.products,
            created_at=order.created_at,
        )

        await self._dynamodb_client.put_item(
            TableName=dynamodb.get_table_name(),
            Item={
                "PK": {"S": f"ORDER#{order.order_id}"},
                "OrderId": {"S": order.order_id},
                "CustomerId": {"S": order.customer_id},
                "Products": {"SS": order.products},
                "CreatedAt": {"S": order.created_at.isoformat()},
            },
            ConditionExpression="attribute_not_exists(PK)",
        )
        await tomodachi.aws_sns_sqs_publish(
            service=self,
            data=event.to_dict(),
            topic="order--created",
            message_envelope=JsonBase,
        )

        logger.info(
            "order_created",
            order_id=order.order_id,
            customer_id=customer_id,
            event_id=event.event_id,
        )
        return web.json_response(order.to_dict())

    @tomodachi.http("GET", r"/order/(?P<order_id>[^/]+?)/?")
    async def get_order(self, request: web.Request, order_id: str) -> web.Response:
        response = await self._dynamodb_client.get_item(
            TableName=dynamodb.get_table_name(),
            Key={"PK": {"S": f"ORDER#{order_id}"}},
        )
        item = response.get("Item")
        if not item:
            logger.error("order_not_found", order_id=order_id)
            return web.json_response({"error": "ORDER_NOT_FOUND"}, status=404)

        order = Order(
            order_id=item["OrderId"]["S"],
            customer_id=item["CustomerId"]["S"],
            products=list(item["Products"]["SS"]),
            created_at=datetime.fromisoformat(item["CreatedAt"]["S"]),
        )

        return web.json_response(order.to_dict())
