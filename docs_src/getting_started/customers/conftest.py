from typing import AsyncGenerator, Generator

import httpx
import pytest
import pytest_asyncio

from tomodachi_testcontainers import DockerContainer, LocalStackContainer, TomodachiContainer
from tomodachi_testcontainers.clients import SNSSQSTestClient


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def _create_topics_and_queues(localstack_snssqs_tc: SNSSQSTestClient) -> None:
    await localstack_snssqs_tc.subscribe_to(topic="customer--created", queue="customer--created")
    await localstack_snssqs_tc.subscribe_to(topic="order--created", queue="customer--order-created")


@pytest_asyncio.fixture(loop_scope="session", autouse=True)
async def _purge_queues_on_teardown(localstack_snssqs_tc: SNSSQSTestClient) -> AsyncGenerator[None, None]:
    yield
    await localstack_snssqs_tc.purge_queue("customer--created")
    await localstack_snssqs_tc.purge_queue("customer--order-created")


@pytest.fixture(scope="session")
def tomodachi_container(
    testcontainer_image: str,
    localstack_container: LocalStackContainer,
    _create_topics_and_queues: None,
) -> Generator[DockerContainer, None, None]:
    with (
        TomodachiContainer(testcontainer_image)
        .with_env("AWS_REGION", "us-east-1")
        .with_env("AWS_ACCESS_KEY_ID", "testing")
        .with_env("AWS_SECRET_ACCESS_KEY", "testing")
        .with_env("AWS_SQS_MAX_RECEIVE_COUNT", "1")
        .with_env("AWS_SQS_VISIBILITY_TIMEOUT", "3")
        .with_env("AWS_SNS_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_env("AWS_SQS_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_env("AWS_DYNAMODB_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_env("DYNAMODB_TABLE_NAME", "autotest-customers")
        .with_command("tomodachi run getting_started/customers/app.py --production")
    ) as container:
        yield container


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def http_client(tomodachi_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        yield client
