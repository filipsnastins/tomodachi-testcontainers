# --8<-- [start:imports]
from types_aiobotocore_dynamodb import DynamoDBClient

from .domain006 import (
    Customer,
    CustomerEmailAlreadyExistsError,
    CustomerIdentifierAlreadyExistsError,
    CustomerNotFoundError,
)

# --8<-- [end:imports]


# --8<-- [start:dynamodb_repository]
class DynamoDBCustomerRepository:
    def __init__(self, client: DynamoDBClient, table_name: str) -> None:
        self._client = client
        self._table_name = table_name

    async def save(self, customer: Customer) -> None:
        try:
            await self._client.transact_write_items(
                TransactItems=[
                    {
                        "Put": {
                            "TableName": self._table_name,
                            "Item": {
                                "PK": {"S": f"CUSTOMER#{customer.id}"},
                                "Id": {"S": customer.id},
                                "Name": {"S": customer.name},
                                "Email": {"S": customer.email},
                            },
                            "ConditionExpression": "attribute_not_exists(PK)",
                        }
                    },
                    {
                        "Put": {
                            "TableName": self._table_name,
                            "Item": {
                                "PK": {"S": f"CUSTOMER#EMAIL#{customer.email}"},
                                "Id": {"S": customer.id},
                                "Email": {"S": customer.email},
                            },
                            "ConditionExpression": "attribute_not_exists(PK)",
                        }
                    },
                ]
            )
        except self._client.exceptions.TransactionCanceledException as e:
            cancellation_reasons = e.response["CancellationReasons"]
            if cancellation_reasons[0]["Code"] == "ConditionalCheckFailed":
                raise CustomerIdentifierAlreadyExistsError(customer.id) from e
            if cancellation_reasons[1]["Code"] == "ConditionalCheckFailed":
                raise CustomerEmailAlreadyExistsError(customer.email) from e
            raise

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


# --8<-- [end:dynamodb_repository]


# --8<-- [start:in_memory_repository]
class InMemoryRepository:
    def __init__(self, customers: list[Customer]) -> None:
        self.customers = {customer.id: customer for customer in customers}

    async def save(self, customer: Customer) -> None:
        if customer.id in self.customers:
            raise CustomerIdentifierAlreadyExistsError(customer.id)
        if customer.email in (customer.email for customer in self.customers.values()):
            raise CustomerEmailAlreadyExistsError(customer.email)
        self.customers[customer.id] = customer

    async def get(self, customer_id: str) -> Customer:
        try:
            return self.customers[customer_id]
        except KeyError as e:
            raise CustomerNotFoundError(customer_id) from e


# --8<-- [end:in_memory_repository]
