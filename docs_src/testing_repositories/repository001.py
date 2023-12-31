from types_aiobotocore_dynamodb import DynamoDBClient

from .domain001 import Customer


class DynamoDBCustomerRepository:
    def __init__(self, client: DynamoDBClient, table_name: str) -> None:
        self._client = client
        self._table_name = table_name

    async def save(self, customer: Customer) -> None:
        await self._client.put_item(
            TableName=self._table_name,
            Item={
                "PK": {"S": f"CUSTOMER#{customer.id}"},
                "Id": {"S": customer.id},
                "Name": {"S": customer.name},
                "Email": {"S": customer.email},
            },
        )
