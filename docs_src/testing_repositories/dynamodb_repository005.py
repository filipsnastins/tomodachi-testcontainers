from types_aiobotocore_dynamodb import DynamoDBClient

from .domain import Customer


class CustomerNotFoundError(Exception):
    pass


class DynamoDBCustomerRepository:
    def __init__(self, client: DynamoDBClient, table_name: str) -> None:
        self._client = client
        self._table_name = table_name

    # --8<-- [start:get]
    async def get(self, customer_id: str) -> Customer:
        response = await self._client.get_item(
            TableName=self._table_name,
            Key={"PK": {"S": f"CUSTOMER#{customer_id}"}},
        )
        item = response.get("Item")
        if item is None:
            raise CustomerNotFoundError(customer_id)
        return Customer(
            id=item["Id"]["S"],
            name=item["Name"]["S"],
            email=item["Email"]["S"],
        )

    # --8<-- [end:get]
