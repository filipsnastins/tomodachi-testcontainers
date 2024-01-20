import os
from typing import AsyncGenerator, Generator, cast

import pytest
import pytest_asyncio
from aiobotocore.session import get_session
from types_aiobotocore_dynamodb import DynamoDBClient
from types_aiobotocore_iam import IAMClient
from types_aiobotocore_lambda import LambdaClient
from types_aiobotocore_s3 import S3Client
from types_aiobotocore_sns import SNSClient
from types_aiobotocore_sqs import SQSClient
from types_aiobotocore_ssm import SSMClient

from .. import LocalStackContainer
from ..clients.snssqs import SNSSQSTestClient


@pytest.fixture(scope="session")
def localstack_container() -> Generator[LocalStackContainer, None, None]:
    image = os.getenv("LOCALSTACK_TESTCONTAINER_IMAGE_ID", "localstack/localstack:3")
    with LocalStackContainer(image) as container:
        yield cast(LocalStackContainer, container)


@pytest.fixture()
def restart_localstack_container_on_teardown(  # noqa: PT004
    localstack_container: LocalStackContainer,
) -> Generator[None, None, None]:
    """Restarts the LocalStack container after each test."""
    yield
    localstack_container.restart()


@pytest_asyncio.fixture(scope="session")
async def localstack_dynamodb_client(localstack_container: LocalStackContainer) -> AsyncGenerator[DynamoDBClient, None]:
    async with get_session().create_client("dynamodb", **localstack_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture(scope="session")
async def localstack_iam_client(localstack_container: LocalStackContainer) -> AsyncGenerator[IAMClient, None]:
    async with get_session().create_client("iam", **localstack_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture(scope="session")
async def localstack_lambda_client(localstack_container: LocalStackContainer) -> AsyncGenerator[LambdaClient, None]:
    async with get_session().create_client("lambda", **localstack_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture(scope="session")
async def localstack_s3_client(localstack_container: LocalStackContainer) -> AsyncGenerator[S3Client, None]:
    async with get_session().create_client("s3", **localstack_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture(scope="session")
async def localstack_sns_client(localstack_container: LocalStackContainer) -> AsyncGenerator[SNSClient, None]:
    async with get_session().create_client("sns", **localstack_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture(scope="session")
async def localstack_sqs_client(localstack_container: LocalStackContainer) -> AsyncGenerator[SQSClient, None]:
    async with get_session().create_client("sqs", **localstack_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture(scope="session")
async def localstack_ssm_client(localstack_container: LocalStackContainer) -> AsyncGenerator[SSMClient, None]:
    async with get_session().create_client("ssm", **localstack_container.get_aws_client_config()) as c:
        yield c


@pytest.fixture(scope="session")
def localstack_snssqs_tc(localstack_sns_client: SNSClient, localstack_sqs_client: SQSClient) -> SNSSQSTestClient:
    return SNSSQSTestClient(localstack_sns_client, localstack_sqs_client)
