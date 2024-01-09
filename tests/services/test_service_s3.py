import uuid
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, Generator, cast

import httpx
import pytest
import pytest_asyncio
from tomodachi.envelope.json_base import JsonBase
from tomodachi_testcontainers import LocalStackContainer, TomodachiContainer
from tomodachi_testcontainers.clients import SNSSQSTestClient
from tomodachi_testcontainers.pytest.assertions import assert_datetime_within_range
from tomodachi_testcontainers.pytest.async_probes import probe_until
from tomodachi_testcontainers.utils import get_available_port
from types_aiobotocore_s3 import S3Client
from types_aiobotocore_sns import SNSClient
from types_aiobotocore_sqs import SQSClient


@pytest.fixture(scope="module")
def snssqs_tc(localstack_sns_client: SNSClient, localstack_sqs_client: SQSClient) -> SNSSQSTestClient:
    return SNSSQSTestClient.create(localstack_sns_client, localstack_sqs_client)


@pytest_asyncio.fixture(scope="module")
async def _create_topics_and_queues(snssqs_tc: SNSSQSTestClient) -> None:
    await snssqs_tc.subscribe_to(topic="s3--file-uploaded", queue="s3--file-uploaded")


@pytest_asyncio.fixture(autouse=True)
async def _purge_queues_on_teardown(snssqs_tc: SNSSQSTestClient) -> AsyncGenerator[None, None]:
    yield
    await snssqs_tc.purge_queue("s3--file-uploaded")


@pytest.fixture(scope="module")
def service_s3_container(
    testcontainers_docker_image: str, localstack_container: LocalStackContainer, _create_topics_and_queues: None
) -> Generator[TomodachiContainer, None, None]:
    with (
        TomodachiContainer(
            image=testcontainers_docker_image,
            edge_port=get_available_port(),
            http_healthcheck_path="/health",
        )
        .with_env("AWS_REGION", "us-east-1")
        .with_env("AWS_ACCESS_KEY_ID", "testing")
        .with_env("AWS_SECRET_ACCESS_KEY", "testing")
        .with_env("AWS_SNS_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_env("AWS_SQS_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_env("AWS_S3_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_env("AWS_S3_BUCKET_NAME", "autotest-filestore")
        .with_env("S3_NOTIFICATION_TOPIC_NAME", "s3--upload-notification")
        .with_command("coverage run -m tomodachi run src/s3.py --production")
    ) as container:
        yield cast(TomodachiContainer, container)


@pytest_asyncio.fixture(scope="module")
async def http_client(service_s3_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=service_s3_container.get_external_url()) as client:
        yield client


@pytest.mark.asyncio()
async def test_file_not_found(http_client: httpx.AsyncClient) -> None:
    response = await http_client.get("/file/not-exists.txt")

    assert response.status_code == 404
    assert response.json() == {
        "error": "File not found",
        "_links": {
            "self": {"href": "/file/not-exists.txt"},
        },
    }


@pytest.mark.asyncio()
async def test_upload_and_read_file(
    http_client: httpx.AsyncClient, localstack_s3_client: S3Client, snssqs_tc: SNSSQSTestClient
) -> None:
    filename = f"{uuid.uuid4()}.txt"
    await localstack_s3_client.put_object(Bucket="autotest-filestore", Key=filename, Body=b"Hello, World!")

    response = await http_client.get(f"/file/{filename}")

    assert response.status_code == 200
    assert response.json() == {
        "content": "Hello, World!",
        "_links": {
            "self": {"href": f"/file/{filename}"},
        },
    }

    async def _file_uploaded_event_emitted() -> Dict[str, Any]:
        [event] = await snssqs_tc.receive("s3--file-uploaded", JsonBase, Dict[str, Any])
        return event

    event = await probe_until(_file_uploaded_event_emitted)
    assert_datetime_within_range(datetime.fromisoformat(event["event_time"]))
    assert event == {
        "uri": f"s3://autotest-filestore/{filename}",
        "eTag": "65a8e27d8879283831b664bd8b7f0ad4",
        "request_id": event["request_id"],
        "event_time": event["event_time"],
    }
