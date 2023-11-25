import os

import structlog
from aiobotocore.session import get_session
from types_aiobotocore_dynamodb import DynamoDBClient

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


def get_table_name() -> str:
    return os.environ["DYNAMODB_TABLE_NAME"]


def get_dynamodb_client() -> DynamoDBClient:
    return get_session().create_client(
        "dynamodb",
        region_name=os.environ["AWS_REGION"],
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.getenv("AWS_DYNAMODB_ENDPOINT_URL"),
    )


async def create_dynamodb_table() -> None:
    table_name = get_table_name()
    log = logger.bind(table_name=table_name)
    async with get_dynamodb_client() as client:
        try:
            await client.create_table(
                TableName=table_name,
                AttributeDefinitions=[
                    {
                        "AttributeName": "PK",
                        "AttributeType": "S",
                    },
                ],
                KeySchema=[
                    {
                        "AttributeName": "PK",
                        "KeyType": "HASH",
                    },
                ],
                BillingMode="PAY_PER_REQUEST",
                StreamSpecification={
                    "StreamEnabled": True,
                    "StreamViewType": "NEW_IMAGE",
                },
            )
        except client.exceptions.ResourceInUseException:
            log.info("dynamodb_table_already_exists")
        else:
            log.info("dynamodb_table_created")
