# --8<-- [start:tomodachi_container]

from typing import AsyncGenerator, Generator, cast

import httpx
import pytest
import pytest_asyncio
from types_aiobotocore_s3 import S3Client

from tomodachi_testcontainers import TomodachiContainer
from tomodachi_testcontainers.containers.moto import MotoContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest_asyncio.fixture(scope="session")
async def _create_s3_buckets(moto_s3_client: S3Client) -> None:
    await moto_s3_client.create_bucket(Bucket="autotest-my-bucket")


@pytest.fixture(scope="session")
def tomodachi_container(
    testcontainers_docker_image: str, moto_container: MotoContainer, _create_s3_buckets: None
) -> Generator[TomodachiContainer, None, None]:
    with (
        TomodachiContainer(image=testcontainers_docker_image, edge_port=get_available_port())
        .with_env("AWS_S3_BUCKET_NAME", "autotest-my-bucket")
        .with_env("AWS_ACCESS_KEY_ID", "testing")
        .with_env("AWS_SECRET_ACCESS_KEY", "testing")
        .with_env("AWS_S3_ENDPOINT_URL", moto_container.get_internal_url())
        .with_command("tomodachi run getting_started/s3/app.py --production")
    ) as container:
        yield cast(TomodachiContainer, container)


# --8<-- [end:tomodachi_container]


@pytest_asyncio.fixture(scope="session")
async def http_client(tomodachi_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        yield client


# --8<-- [start:test_save_and_get_file]

import uuid


@pytest.mark.parametrize("content", ["Hello, world!", "Multi\nline\nfile"])
@pytest.mark.asyncio()
async def test_save_and_get_file(http_client: httpx.AsyncClient, content: str) -> None:
    filename = f"test-{uuid.uuid4()}.txt"

    response = await http_client.post("/file/", json={"filename": filename, "content": content})
    assert response.status_code == 200
    assert response.json() == {"key": filename}

    response = await http_client.get(f"/file/{filename}")
    assert response.status_code == 200
    assert response.json() == {"content": content}


# --8<-- [end:test_save_and_get_file]


# --8<-- [start:test_file_not_found]
@pytest.mark.asyncio()
async def test_file_not_found(http_client: httpx.AsyncClient) -> None:
    response = await http_client.get("/file/not-found.txt")

    assert response.status_code == 404
    assert response.json() == {"error": "File not found"}


# --8<-- [end:test_file_not_found]
