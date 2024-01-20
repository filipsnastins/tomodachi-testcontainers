import os

import structlog
from types_aiobotocore_dynamodb import DynamoDBClient

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


def get_table_name() -> str:
    return os.environ["DYNAMODB_TABLE_NAME"]


async def create_dynamodb_table(client: DynamoDBClient) -> None:
    table_name = get_table_name()
    log = logger.bind(table_name=table_name)
    try:
        await client.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
            ],
            BillingMode="PAY_PER_REQUEST",
            StreamSpecification={"StreamEnabled": True, "StreamViewType": "NEW_IMAGE"},
        )
    except client.exceptions.ResourceInUseException:
        log.info("dynamodb_table_already_exists")
    else:
        log.info("dynamodb_table_created")
