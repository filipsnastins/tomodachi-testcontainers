# --8<-- [start:create_s3_buckets]
import pytest_asyncio
from types_aiobotocore_s3 import S3Client


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def _create_s3_buckets(localstack_s3_client: S3Client) -> None:
    await localstack_s3_client.create_bucket(Bucket="autotest-my-bucket")


# --8<-- [end:create_s3_buckets]


from typing import Generator

import pytest

from tomodachi_testcontainers import DockerContainer, LocalStackContainer, TomodachiContainer


# --8<-- [start:tomodachi_container]
@pytest.fixture(scope="session")
def tomodachi_container(
    testcontainer_image: str,
    localstack_container: LocalStackContainer,
    _create_s3_buckets: None,
) -> Generator[DockerContainer, None, None]:
    # --8<-- [end:tomodachi_container]
    with (
        TomodachiContainer(testcontainer_image)
        .with_env("AWS_S3_BUCKET_NAME", "autotest-my-bucket")
        .with_env("AWS_ACCESS_KEY_ID", "testing")
        .with_env("AWS_SECRET_ACCESS_KEY", "testing")
        .with_env("AWS_S3_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_command("tomodachi run getting_started/s3/app.py --production")
    ) as container:
        yield container


# --8<-- [start:test_save_and_get_file]
import httpx
import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_save_and_get_file(http_client: httpx.AsyncClient) -> None:
    response = await http_client.post("/file/", json={"filename": "test.txt", "content": "Hello, world!"})
    assert response.status_code == 200
    assert response.json() == {"key": "test.txt"}

    response = await http_client.get("/file/test.txt")
    assert response.status_code == 200
    assert response.json() == {"content": "Hello, world!"}


# --8<-- [end:test_save_and_get_file]


# --8<-- [start:test_file_not_found]
@pytest.mark.asyncio(loop_scope="session")
async def test_file_not_found(http_client: httpx.AsyncClient) -> None:
    response = await http_client.get("/file/not-exists.txt")

    assert response.status_code == 404
    assert response.json() == {"error": "FILE_NOT_FOUND"}


# --8<-- [end:test_file_not_found]
