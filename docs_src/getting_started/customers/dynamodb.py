import os
from contextlib import suppress

from types_aiobotocore_dynamodb import DynamoDBClient


def get_table_name() -> str:
    return os.environ["DYNAMODB_TABLE_NAME"]


async def create_dynamodb_table(client: DynamoDBClient) -> None:
    with suppress(client.exceptions.ResourceInUseException):
        await client.create_table(
            TableName=get_table_name(),
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
