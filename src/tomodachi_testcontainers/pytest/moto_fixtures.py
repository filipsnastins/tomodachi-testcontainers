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

from tomodachi_testcontainers.containers import MotoContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture(scope="session")
def moto_container() -> Generator[MotoContainer, None, None]:
    image = os.environ.get("MOTO_TESTCONTAINER_IMAGE_ID", "motoserver/moto:latest")
    with MotoContainer(image=image, edge_port=get_available_port()) as container:
        yield container


@pytest.fixture()
def _reset_moto_container(moto_container: MotoContainer) -> Generator[None, None, None]:
    yield
    moto_container.reset()


@pytest_asyncio.fixture()
async def moto_sns_client(moto_container: MotoContainer) -> AsyncGenerator[SNSClient, None]:
    async with get_session().create_client("sns", **moto_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture()
async def moto_sqs_client(moto_container: MotoContainer) -> AsyncGenerator[SQSClient, None]:
    async with get_session().create_client("sqs", **moto_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture()
async def moto_s3_client(moto_container: MotoContainer) -> AsyncGenerator[S3Client, None]:
    async with get_session().create_client("s3", **moto_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture()
async def moto_dynamodb_client(moto_container: MotoContainer) -> AsyncGenerator[DynamoDBClient, None]:
    async with get_session().create_client("dynamodb", **moto_container.get_aws_client_config()) as c:
        yield c


@pytest_asyncio.fixture()
async def moto_ssm_client(moto_container: MotoContainer) -> AsyncGenerator[SSMClient, None]:
    async with get_session().create_client("ssm", **moto_container.get_aws_client_config()) as c:
        yield c
