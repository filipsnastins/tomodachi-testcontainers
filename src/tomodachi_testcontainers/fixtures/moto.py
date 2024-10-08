import os
from typing import AsyncGenerator, Generator

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

from .. import DockerContainer, MotoContainer
from ..clients.snssqs import SNSSQSTestClient


@pytest.fixture(scope="session")
def moto_container() -> Generator[DockerContainer, None, None]:
    image = os.getenv("MOTO_TESTCONTAINER_IMAGE_ID", "motoserver/moto:latest")
    disable_logging = bool(os.getenv("MOTO_TESTCONTAINER_DISABLE_LOGGING")) or False

    with MotoContainer(image, disable_logging=disable_logging) as container:
        yield container


@pytest.fixture
def reset_moto_container_on_teardown(moto_container: MotoContainer) -> Generator[None, None, None]:  # noqa: PT004
    """Removes all mocked resources from Moto after each test without restarting the container."""
    yield
    moto_container.reset_moto()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def moto_dynamodb_client(moto_container: MotoContainer) -> AsyncGenerator[DynamoDBClient, None]:
    async with get_session().create_client("dynamodb", **moto_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def moto_iam_client(moto_container: MotoContainer) -> AsyncGenerator[IAMClient, None]:
    async with get_session().create_client("iam", **moto_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def moto_lambda_client(moto_container: MotoContainer) -> AsyncGenerator[LambdaClient, None]:
    async with get_session().create_client("lambda", **moto_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def moto_s3_client(moto_container: MotoContainer) -> AsyncGenerator[S3Client, None]:
    async with get_session().create_client("s3", **moto_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def moto_sns_client(moto_container: MotoContainer) -> AsyncGenerator[SNSClient, None]:
    async with get_session().create_client("sns", **moto_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def moto_sqs_client(moto_container: MotoContainer) -> AsyncGenerator[SQSClient, None]:
    async with get_session().create_client("sqs", **moto_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def moto_ssm_client(moto_container: MotoContainer) -> AsyncGenerator[SSMClient, None]:
    async with get_session().create_client("ssm", **moto_container.get_aws_client_config()) as c:
        yield c


@pytest.fixture(scope="session")
def moto_snssqs_tc(moto_sns_client: SNSClient, moto_sqs_client: SQSClient) -> SNSSQSTestClient:
    return SNSSQSTestClient(moto_sns_client, moto_sqs_client)
