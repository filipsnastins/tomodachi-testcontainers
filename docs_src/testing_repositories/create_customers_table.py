from types_aiobotocore_dynamodb import DynamoDBClient


async def create_customers_table(client: DynamoDBClient, table_name: str) -> None:
    await client.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
