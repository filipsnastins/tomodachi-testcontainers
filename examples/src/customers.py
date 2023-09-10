import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List

import structlog
import tomodachi
from adapters import dynamodb
from aiohttp import web
from pydantic import BaseModel
from tomodachi.envelope.json_base import JsonBase
from utils.logger import configure_logger

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class Order(BaseModel):
    order_id: str

    def to_json_dict(self) -> Dict:
        return {"order_id": self.order_id}


class OrderCreatedEvent(BaseModel):
    event_id: str
    order_id: str
    customer_id: str

    @staticmethod
    def from_dict(event: Dict) -> "OrderCreatedEvent":
        return OrderCreatedEvent(
            event_id=event["event_id"],
            order_id=event["order_id"],
            customer_id=event["customer_id"],
        )


class Customer(BaseModel):
    customer_id: str
    name: str
    orders: List[Order]
    created_at: datetime

    def to_json_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "orders": [order.to_json_dict() for order in self.orders],
            "created_at": self.created_at.isoformat(),
        }


class TomodachiServiceCustomers(tomodachi.Service):
    name = "service-customers"

    options = tomodachi.Options(
        aws_endpoint_urls=tomodachi.Options.AWSEndpointURLs(
            sns=os.getenv("AWS_SNS_ENDPOINT_URL"),
            sqs=os.getenv("AWS_SQS_ENDPOINT_URL"),
        ),
        aws_sns_sqs=tomodachi.Options.AWSSNSSQS(
            region_name=os.environ["AWS_REGION"],
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            topic_prefix=os.getenv("AWS_SNS_TOPIC_PREFIX", ""),
            queue_name_prefix=os.getenv("AWS_SQS_QUEUE_NAME_PREFIX", ""),
        ),
    )

    async def _start_service(self) -> None:
        configure_logger()
        await dynamodb.create_dynamodb_table()

    @tomodachi.http("GET", r"/health/?")
    async def healthcheck(self, request: web.Request) -> web.Response:
        return web.json_response(data={"status": "ok"})

    @tomodachi.http("POST", r"/customers")
    async def create_customer(self, request: web.Request) -> web.Response:
        data = await request.json()

        customer = Customer(
            customer_id=str(uuid.uuid4()),
            name=data["name"],
            orders=[],
            created_at=datetime.utcnow().replace(tzinfo=timezone.utc),
        )

        async with dynamodb.get_dynamodb_client() as dynamodb_client:
            await dynamodb_client.put_item(
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
        return web.json_response(
            {
                "customer_id": customer.customer_id,
                "_links": {
                    "self": {"href": f"/customer/{customer.customer_id}"},
                },
            }
        )

    @tomodachi.http("GET", r"/customer/(?P<customer_id>[^/]+?)/?")
    async def get_customer(self, request: web.Request, customer_id: str) -> web.Response:
        links = {
            "_links": {
                "self": {"href": f"/customer/{customer_id}"},
            }
        }
        async with dynamodb.get_dynamodb_client() as dynamodb_client:
            response = await dynamodb_client.get_item(
                TableName=dynamodb.get_table_name(), Key={"PK": {"S": f"CUSTOMER#{customer_id}"}}
            )
            if "Item" not in response:
                logger.error("customer_not_found", customer_id=customer_id)
                return web.json_response({"error": "Customer not found", **links}, status=404)

            item = response["Item"]
            orders = item["Orders"]["SS"] if "Orders" in item else []
            customer = Customer(
                customer_id=item["CustomerId"]["S"],
                name=item["Name"]["S"],
                orders=[Order(order_id=order_id) for order_id in orders],
                created_at=datetime.fromisoformat(item["CreatedAt"]["S"]),
            )

        return web.json_response({**customer.to_json_dict(), **links})

    @tomodachi.aws_sns_sqs(
        "order--created",
        queue_name="customer--order-created",
        message_envelope=JsonBase,
    )
    async def handle_order_created(self, data: Dict) -> None:
        event = OrderCreatedEvent.from_dict(data)

        async with dynamodb.get_dynamodb_client() as dynamodb_client:
            await dynamodb_client.update_item(
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
