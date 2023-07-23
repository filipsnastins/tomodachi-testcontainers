from datetime import datetime
from typing import Any, AsyncGenerator, Dict, Generator, cast

import httpx
import pytest
import pytest_asyncio
from busypie import wait_at_most
from docker.models.images import Image as DockerImage
from tomodachi.envelope.json_base import JsonBase
from types_aiobotocore_s3 import S3Client
from types_aiobotocore_sns import SNSClient
from types_aiobotocore_sqs import SQSClient

from tomodachi_testcontainers.clients import snssqs_client
from tomodachi_testcontainers.containers import LocalStackContainer, TomodachiContainer
from tomodachi_testcontainers.pytest.assertions import assert_datetime_within_range
from tomodachi_testcontainers.utils import get_available_port


@pytest_asyncio.fixture()
async def _create_topics_and_queues(localstack_sns_client: SNSClient, localstack_sqs_client: SQSClient) -> None:
    await snssqs_client.subscribe_to(
        localstack_sns_client,
        localstack_sqs_client,
        topic="s3--file-uploaded",
        queue="s3--file-uploaded",
    )


@pytest.fixture()
def service_s3_container(
    tomodachi_image: DockerImage,
    localstack_container: LocalStackContainer,
    _restart_localstack_container: None,
    _create_topics_and_queues: None,
) -> Generator[TomodachiContainer, None, None]:
    with (
        TomodachiContainer(image=str(tomodachi_image.id), edge_port=get_available_port())
        .with_env("AWS_REGION", "eu-west-1")
        .with_env("AWS_ACCESS_KEY_ID", "testing")
        .with_env("AWS_SECRET_ACCESS_KEY", "testing")
        .with_env("AWS_SNS_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_env("AWS_SQS_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_env("AWS_S3_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_env("S3_BUCKET_NAME", "filestore")
        .with_env("S3_NOTIFICATION_TOPIC_NAME", "s3--upload-notification")
        .with_command("tomodachi run src/s3.py --production")
    ) as container:
        yield cast(TomodachiContainer, container)


@pytest_asyncio.fixture()
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
    http_client: httpx.AsyncClient, localstack_s3_client: S3Client, localstack_sqs_client: SQSClient
) -> None:
    await localstack_s3_client.put_object(Bucket="filestore", Key="hello-world.txt", Body=b"Hello, World!")

    response = await http_client.get("/file/hello-world.txt")

    assert response.status_code == 200
    assert response.json() == {
        "content": "Hello, World!",
        "_links": {
            "self": {"href": "/file/hello-world.txt"},
        },
    }

    async def _file_uploaded_event_emitted() -> None:
        [event] = await snssqs_client.receive(localstack_sqs_client, "s3--file-uploaded", JsonBase, Dict[str, Any])

        assert_datetime_within_range(datetime.fromisoformat(event["event_time"]))
        assert event == {
            "uri": "s3://filestore/hello-world.txt",
            "eTag": "65a8e27d8879283831b664bd8b7f0ad4",
            "request_id": event["request_id"],
            "event_time": event["event_time"],
        }

    await wait_at_most(5).until_asserted_async(_file_uploaded_event_emitted)


@pytest.mark.asyncio()
async def test_data_does_not_persist_between_tests(http_client: httpx.AsyncClient) -> None:
    response = await http_client.get("/file/hello-world.txt")

    assert response.status_code == 404
    assert response.json() == {
        "error": "File not found",
        "_links": {
            "self": {"href": "/file/hello-world.txt"},
        },
    }
