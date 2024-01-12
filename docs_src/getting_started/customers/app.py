import os
import uuid
from typing import Dict

import tomodachi
from aiohttp import web
from tomodachi.envelope.json_base import JsonBase

from . import aws, dynamodb
from .domain import Customer, CustomerCreatedEvent, OrderCreatedEvent
from .repository import DynamoDBCustomerRepository


class Service(tomodachi.Service):
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
        self._dynamodb_client, self._dynamodb_client_exit_stack = await aws.create_dynamodb_client()
        self._repository = DynamoDBCustomerRepository(self._dynamodb_client, dynamodb.get_table_name())
        await dynamodb.create_dynamodb_table(self._dynamodb_client)

    async def _stop_service(self) -> None:
        await self._dynamodb_client_exit_stack.aclose()

    @tomodachi.http("POST", r"/customer/?")
    async def create_customer(self, request: web.Request) -> web.Response:
        data = await request.json()
        customer = Customer(
            customer_id=str(uuid.uuid4()),
            name=data["name"],
            orders=[],
        )
        event = CustomerCreatedEvent.from_customer(customer)
        await self._repository.create(customer)
        await tomodachi.aws_sns_sqs_publish(
            self,
            data=event.to_dict(),
            topic="customer--created",
            message_envelope=JsonBase,
        )
        return web.json_response(customer.to_dict())

    @tomodachi.http("GET", r"/customer/(?P<customer_id>[^/]+?)/?")
    async def get_customer(self, request: web.Request, customer_id: str) -> web.Response:
        customer = await self._repository.get(customer_id)
        if not customer:
            return web.json_response({"error": "CUSTOMER_NOT_FOUND"}, status=404)
        return web.json_response(customer.to_dict())

    @tomodachi.aws_sns_sqs(
        "order--created",
        queue_name="customer--order-created",
        message_envelope=JsonBase,
    )
    async def handle_order_created(self, data: Dict) -> None:
        event = OrderCreatedEvent.from_dict(data)
        await self._repository.add_order(event)
