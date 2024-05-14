import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from aiobotocore.session import get_session
from types_aiobotocore_s3 import S3Client

from .. import DockerContainer, MinioContainer


@pytest.fixture(scope="session")
def minio_container() -> Generator[DockerContainer, None, None]:
    image = os.getenv("MINIO_TESTCONTAINER_IMAGE_ID", "minio/minio:latest")
    disable_logging = bool(os.getenv("MINIO_TESTCONTAINER_DISABLE_LOGGING", False))

    with MinioContainer(image, disable_logging=disable_logging) as container:
        yield container


@pytest_asyncio.fixture(scope="session")
async def minio_s3_client(minio_container: MinioContainer) -> AsyncGenerator[S3Client, None]:
    async with get_session().create_client("s3", **minio_container.get_aws_client_config()) as c:
        yield c
