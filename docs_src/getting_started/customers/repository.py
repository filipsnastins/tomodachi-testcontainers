from typing import Optional

from types_aiobotocore_dynamodb import DynamoDBClient

from .domain import Customer, Order, OrderCreatedEvent


class CustomerIdentifierAlreadyExistsError(Exception):
    pass


class CustomerNotFoundError(Exception):
    pass


class DynamoDBCustomerRepository:
    def __init__(self, client: DynamoDBClient, table_name: str) -> None:
        self._client = client
        self._table_name = table_name

    async def create(self, customer: Customer) -> None:
        try:
            await self._client.put_item(
                TableName=self._table_name,
                Item={
                    "PK": {"S": f"CUSTOMER#{customer.customer_id}"},
                    "CustomerId": {"S": customer.customer_id},
                    "Name": {"S": customer.name},
                },
                ConditionExpression="attribute_not_exists(PK)",
            )
        except self._client.exceptions.ConditionalCheckFailedException:
            raise CustomerIdentifierAlreadyExistsError(customer.customer_id)

    async def get(self, customer_id: str) -> Optional[Customer]:
        response = await self._client.get_item(
            TableName=self._table_name,
            Key={"PK": {"S": f"CUSTOMER#{customer_id}"}},
        )
        item = response.get("Item")
        if not item:
            return None
        orders = item["Orders"]["SS"] if "Orders" in item else []
        return Customer(
            customer_id=item["CustomerId"]["S"],
            name=item["Name"]["S"],
            orders=[Order(order_id=order_id) for order_id in orders],
        )

    async def add_order(self, event: OrderCreatedEvent) -> None:
        try:
            await self._client.update_item(
                TableName=self._table_name,
                Key={"PK": {"S": f"CUSTOMER#{event.customer_id}"}},
                UpdateExpression="ADD Orders :orders",
                ExpressionAttributeValues={":orders": {"SS": [event.order_id]}},
                ConditionExpression="attribute_exists(PK)",
            )
        except self._client.exceptions.ConditionalCheckFailedException:
            raise CustomerNotFoundError(event.customer_id)
