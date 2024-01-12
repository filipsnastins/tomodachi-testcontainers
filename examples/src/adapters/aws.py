import os
from contextlib import AsyncExitStack
from typing import Tuple

from aiobotocore.session import get_session
from types_aiobotocore_dynamodb import DynamoDBClient
from types_aiobotocore_s3 import S3Client
from types_aiobotocore_sns import SNSClient

session = get_session()


async def create_s3_client() -> Tuple[S3Client, AsyncExitStack]:
    exit_stack = AsyncExitStack()
    client = await exit_stack.enter_async_context(
        session.create_client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL"),
        )
    )
    return client, exit_stack


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


async def create_sns_client() -> Tuple[SNSClient, AsyncExitStack]:
    exit_stack = AsyncExitStack()
    client = await exit_stack.enter_async_context(
        session.create_client(
            "sns",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.environ["AWS_REGION"],
            endpoint_url=os.getenv("AWS_SNS_ENDPOINT_URL"),
        )
    )
    return client, exit_stack
