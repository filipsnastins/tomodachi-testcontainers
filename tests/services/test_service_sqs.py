from typing import Generator

import pytest
from tomodachi.envelope.json_base import JsonBase

from tomodachi_testcontainers import DockerContainer, LocalStackContainer, TomodachiContainer
from tomodachi_testcontainers.assertions import assert_logs_contain
from tomodachi_testcontainers.async_probes import probe_until
from tomodachi_testcontainers.clients import SNSSQSTestClient


@pytest.fixture(scope="module")
def tomodachi_container(
    testcontainer_image: str, localstack_container: LocalStackContainer
) -> Generator[DockerContainer, None, None]:
    with (
        TomodachiContainer(testcontainer_image, http_healthcheck_path="/health")
        .with_env("AWS_REGION", "us-east-1")
        .with_env("AWS_ACCESS_KEY_ID", "testing")
        .with_env("AWS_SECRET_ACCESS_KEY", "testing")
        .with_env("AWS_SQS_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_command("coverage run -m tomodachi run src/sqs.py --production")
    ) as container:
        yield container


@pytest.mark.asyncio
async def test_send_sqs_message(
    tomodachi_container: TomodachiContainer, localstack_snssqs_tc: SNSSQSTestClient
) -> None:
    await localstack_snssqs_tc.send(queue="test-queue", data={"foo": "bar"}, envelope=JsonBase)

    await probe_until(lambda: assert_logs_contain(tomodachi_container, "message_received"))
