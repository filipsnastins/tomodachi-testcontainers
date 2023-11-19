import os
from typing import AsyncGenerator, Generator, cast

import pytest
import pytest_asyncio
from aiobotocore.session import get_session
from types_aiobotocore_s3 import S3Client

from tomodachi_testcontainers import MinioContainer
from tomodachi_testcontainers.utils import get_available_port


@pytest.fixture(scope="session")
def minio_container() -> Generator[MinioContainer, None, None]:
    image = os.getenv("MINIO_TESTCONTAINER_IMAGE_ID", "minio/minio:latest")
    with MinioContainer(
        image=image,
        s3_api_edge_port=get_available_port(),
        console_edge_port=get_available_port(),
    ) as container:
        yield cast(MinioContainer, container)


@pytest_asyncio.fixture(scope="session")
async def minio_s3_client(minio_container: MinioContainer) -> AsyncGenerator[S3Client, None]:
    async with get_session().create_client("s3", **minio_container.get_aws_client_config()) as c:
        yield c
