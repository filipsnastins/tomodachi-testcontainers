from typing import AsyncGenerator, Generator, cast

import httpx
import pytest
import pytest_asyncio

from tomodachi_testcontainers import LocalStackContainer, TomodachiContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture(scope="session")
def tomodachi_container(
    testcontainer_image: str,
    localstack_container: LocalStackContainer,
) -> Generator[TomodachiContainer, None, None]:
    with (
        TomodachiContainer(
            image=testcontainer_image,
            edge_port=get_available_port(),
        )
        .with_env("AWS_S3_BUCKET_NAME", "autotest-my-bucket")
        .with_env("AWS_ACCESS_KEY_ID", "testing")
        .with_env("AWS_SECRET_ACCESS_KEY", "testing")
        .with_env("AWS_S3_ENDPOINT_URL", localstack_container.get_internal_url())
        .with_command("tomodachi run getting_started/s3/app.py --production")
    ) as container:
        yield cast(TomodachiContainer, container)


@pytest_asyncio.fixture(scope="session")
async def http_client(tomodachi_container: TomodachiContainer) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=tomodachi_container.get_external_url()) as client:
        yield client
