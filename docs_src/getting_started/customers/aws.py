import os
from contextlib import AsyncExitStack
from typing import Tuple

from aiobotocore.session import get_session
from types_aiobotocore_dynamodb import DynamoDBClient

session = get_session()


async def create_dynamodb_client() -> Tuple[DynamoDBClient, AsyncExitStack]:
    exit_stack = AsyncExitStack()
    client = await exit_stack.enter_async_context(
        session.create_client(
            "dynamodb",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.environ["AWS_REGION"],
            endpoint_url=os.getenv("AWS_DYNAMODB_ENDPOINT_URL"),
        )
    )
    return client, exit_stack
