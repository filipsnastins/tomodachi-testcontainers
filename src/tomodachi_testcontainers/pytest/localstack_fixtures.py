import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from aiobotocore.session import get_session
from types_aiobotocore_dynamodb import DynamoDBClient
from types_aiobotocore_s3 import S3Client
from types_aiobotocore_sns import SNSClient
from types_aiobotocore_sqs import SQSClient
from types_aiobotocore_ssm import SSMClient

from tomodachi_testcontainers.containers import LocalStackContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture(scope="session")
def localstack_container() -> Generator[LocalStackContainer, None, None]:
    image = os.environ.get("LOCALSTACK_TESTCONTAINER_IMAGE_ID", "localstack/localstack:2.1")
    with LocalStackContainer(image=image, edge_port=get_available_port()) as container:
        yield container


@pytest.fixture()
def _restart_localstack_container(localstack_container: LocalStackContainer) -> Generator[None, None, None]:
    yield
    localstack_container.restart()


@pytest_asyncio.fixture()
async def localstack_sns_client(localstack_container: LocalStackContainer) -> AsyncGenerator[SNSClient, None]:
    async with get_session().create_client("sns", **localstack_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture()
async def localstack_sqs_client(localstack_container: LocalStackContainer) -> AsyncGenerator[SQSClient, None]:
    async with get_session().create_client("sqs", **localstack_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture()
async def localstack_s3_client(localstack_container: LocalStackContainer) -> AsyncGenerator[S3Client, None]:
    async with get_session().create_client("s3", **localstack_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture()
async def localstack_dynamodb_client(localstack_container: LocalStackContainer) -> AsyncGenerator[DynamoDBClient, None]:
    async with get_session().create_client("dynamodb", **localstack_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture()
async def localstack_ssm_client(localstack_container: LocalStackContainer) -> AsyncGenerator[SSMClient, None]:
    async with get_session().create_client("ssm", **localstack_container.get_aws_client_config()) as c:
        yield c
